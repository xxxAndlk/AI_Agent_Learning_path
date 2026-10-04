# -*- coding: utf-8 -*-
# 用途：演示"让模型记得前文"——新版 checkpointer + thread_id 连问两轮证明它记得，
#       并附旧版 BufferMemory 写法对照；末尾带一个不依赖框架、纯标准库可真跑的离线小练。
# pip install langchain langchain-openai langchain-core python-dotenv
# 运行前配置环境变量 OPENAI_API_KEY（或在本文件同目录建 .env 写 OPENAI_API_KEY=sk-...，
# .env 不要提交到代码仓库）。
# 注意：在线部分需要 API Key 且产生少量费用，本机未实跑；离线小练无 Key 也能跑。

import os

# 可选：装了 python-dotenv 就从 .env 读 Key；没装也不影响
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# ---------------------------------------------------------------- 新范式（2026 主流）
def demo_new_checkpointer() -> None:
    """给 Agent 配一个 checkpointer，同一 thread_id 它就记得前文。"""
    from langchain.agents import create_agent
    from langchain_openai import ChatOpenAI
    from langgraph.checkpoint.memory import InMemorySaver

    checkpointer = InMemorySaver()  # 存内存：程序重启就没了；要跨重启换 SQLite 等实现
    agent = create_agent(
        model=ChatOpenAI(model="gpt-4o-mini"),  # 示例名，实际按官网模型列表选当前便宜够用的
        tools=[],
        system_prompt="你是一个友好的中文助手，回答简短。",
        checkpointer=checkpointer,
    )
    config = {"configurable": {"thread_id": "chat-1"}}  # 同一段对话共用一个线程号

    r1 = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫小林，最喜欢的数字是 7。"}]},
        config,
    )
    print("第1轮回答：", r1["messages"][-1].content)

    r2 = agent.invoke(
        {"messages": [{"role": "user", "content": "我叫什么名字？最喜欢哪个数字？"}]},
        config,
    )
    print("第2轮回答：", r2["messages"][-1].content)
    print("→ 第2轮答得上，说明同一 thread_id 的历史被自动装进了提示。\n")


# ---------------------------------------------------------------- 旧范式（对照用）
def demo_old_memory_note() -> None:
    """旧版 ConversationBufferMemory 写法已进维护模式，老教程常见，这里注释保留对照。"""
    print("（旧范式写法对照，见下方注释，新项目不建议再从它起步）\n")
    # from langchain.memory import ConversationBufferMemory
    # from langchain.chains import ConversationChain
    # from langchain_openai import ChatOpenAI
    #
    # memory = ConversationBufferMemory()          # 原文全留：越攒越长、费 token
    # conversation = ConversationChain(
    #     llm=ChatOpenAI(model="gpt-4o-mini"),
    #     memory=memory,
    # )
    # conversation.predict(input="我叫小林，最喜欢的数字是 7。")
    # conversation.predict(input="我叫什么名字？最喜欢哪个数字？")  # 它答得上
    #
    # 同族的 ConversationBufferWindowMemory(k=3) 只留最近 3 轮，
    # ConversationSummaryMemory(llm=...) 用 LLM 把旧对话压成摘要——取舍思路见讲义第三、四节。


# ---------------------------------------------------------------- 离线小练（无 Key 可跑）
def window_recent_rounds(history: list[dict], k: int = 2) -> list[dict]:
    """窗口策略：只保留最近 k 轮。一轮 = 一问一答两条消息。"""
    return history[-2 * k :]


def brief_summary(history: list[dict]) -> str:
    """摘要策略的极简版：把每条消息压成一行拼接梗概（真实做法是用 LLM 压缩）。"""
    who = {"user": "用户", "ai": "AI"}
    return "；".join(f"{who[m['role']]}说：{m['content']}" for m in history)


def offline_practice() -> None:
    """手写一份消息历史，对比三种留历史的策略——不依赖框架，纯标准库可真跑。"""
    history = [
        {"role": "user", "content": "我叫小林，最喜欢的数字是 7。"},
        {"role": "ai", "content": "你好小林！7 是个幸运数字。"},
        {"role": "user", "content": "帮我记一下：周五要交周报。"},
        {"role": "ai", "content": "好的，已记住：周五交周报。"},
        {"role": "user", "content": "再记一条：周六上午看牙医。"},
        {"role": "ai", "content": "记下了：周六上午看牙医。"},
    ]

    print("原始历史共", len(history), "条消息（缓冲策略：6 条全留）\n")

    recent = window_recent_rounds(history, k=2)
    print("窗口策略（只留最近 2 轮）后剩", len(recent), "条：")
    for m in recent:
        print("  -", m["content"])
    print("  → 「小林」已经不在列表里了：早前提的事真的会忘。\n")

    print("摘要策略（简单拼接梗概）：")
    print("  ", brief_summary(history))
    print("  → 一行装下全部 6 条的大意；细节是否保留，取决于摘要压缩到多狠。\n")


def main() -> None:
    print("== Memory 演示：让模型记得前文 ==\n")
    offline_practice()  # 纯标准库，总是能跑

    if not os.environ.get("OPENAI_API_KEY"):
        print("未检测到环境变量 OPENAI_API_KEY，在线演示跳过。")
        print("配置方法：set OPENAI_API_KEY=sk-...（Windows）或 export OPENAI_API_KEY=sk-...（Mac/Linux），")
        print("或在同目录建 .env 文件写入 OPENAI_API_KEY=sk-...。上面的离线小练已完整演示三种策略。")
        return

    try:
        demo_new_checkpointer()
        demo_old_memory_note()
    except Exception as exc:  # 网络/Key/额度等运行期问题，给人话不甩堆栈
        print(f"在线演示没跑成（常见原因：网络不通、Key 无效、额度用尽）：{exc}")
        print("不影响上面的离线小练结论。")


if __name__ == "__main__":
    main()
