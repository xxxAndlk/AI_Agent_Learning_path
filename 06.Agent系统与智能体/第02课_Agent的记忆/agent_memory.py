# -*- coding: utf-8 -*-
# 用途：演示 Agent 的记忆——短期记忆怎么攒、怎么被窗口截断、跨会话怎么隔离。
# 依赖：第 1 部分仅 Python 标准库；第 2 部分需 pip install openai langchain langgraph
#       （缺库或缺 API Key 会打印中文提示并优雅跳过；真实调用段需 Key，未实跑）

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台防中文乱码
except Exception:
    pass

# ---------- 第 1 部分：纯标准库，离线真跑 ----------

def fake_llm(messages):
    """假模型：它本身毫无记忆，能'记得'，全靠我们把历史完整发给它。"""
    text = messages[-1]["content"]
    if "我叫" in text and "什么" not in text and "谁" not in text:
        name = text.split("我叫")[1].split("，")[0].strip()
        return f"你好，{name}！很高兴认识你。"
    if "我叫什么" in text or "我是谁" in text:
        for m in reversed(messages[:-1]):          # 在历史里翻名字
            if m["role"] == "user" and "我叫" in m["content"] and "什么" not in m["content"]:
                name = m["content"].split("我叫")[1].split("，")[0].strip()
                return f"你叫{name}呀，我们聊过！"
        return "这个我还真不知道——你没告诉过我。"
    return "收到，继续聊。"

# 短期记忆仓库：thread_id -> 消息列表。真实框架里它由 checkpointer 替你保管。
MEMORY_STORE = {}

def chat(thread_id, text, send_history=True, window=None):
    """一轮对话：把历史（或窗口内历史）连同新消息一起发给'模型'。"""
    msgs = MEMORY_STORE.setdefault(thread_id, [])
    msgs.append({"role": "user", "content": text})
    if send_history:
        sent = msgs if window is None else msgs[-window:]
    else:
        sent = [msgs[-1]]                          # 只发最后一条：模型立刻"失忆"
    reply = fake_llm(sent)
    msgs.append({"role": "assistant", "content": reply})
    return reply, len(sent)

def part1_offline():
    print("=" * 52)
    print("实验1：同一会话连着聊（短期记忆 = 完整历史）")
    r, n = chat("user-A", "我叫小明，今年28岁，在杭州做程序员")
    print(f"  [发给模型 {n} 条历史] 助手：{r}")
    r, n = chat("user-A", "你还记得我叫什么吗？")
    print(f"  [发给模型 {n} 条历史] 助手：{r}")

    print("\n实验2：换个会话直接问（thread_id 隔离，各聊各的）")
    r, n = chat("user-B", "你还记得我叫什么吗？")
    print(f"  [发给模型 {n} 条历史] 助手：{r}")

    print("\n实验3：窗口截断——只发最近 2 条，Agent 开始'失忆'")
    chat("user-A", "今天杭州天气怎么样？")
    chat("user-A", "帮我推荐一首歌")
    r, n = chat("user-A", "你还记得我叫什么吗？", window=2)
    print(f"  [发给模型 {n} 条历史] 助手：{r}")

    print("\n实验4：只发最后一条（证明记忆不在模型里）")
    r, n = chat("user-A", "你还记得我叫什么吗？", send_history=False)
    print(f"  [发给模型 {n} 条历史] 助手：{r}")
    print("\n当前记忆仓库：", {k: len(v) for k, v in MEMORY_STORE.items()})

# ---------- 第 2 部分：2026 主流范式（需第三方库与 API Key，未实跑） ----------

def part2_real_framework():
    """create_agent + checkpointer + 同一 thread_id，记忆就跨轮保留。"""
    try:
        from langchain.agents import create_agent
        from langgraph.checkpoint.memory import InMemorySaver
    except ImportError:
        print("[跳过] 第2部分需要：pip install openai langchain langgraph")
        return
    import os
    if not os.environ.get("OPENAI_API_KEY"):
        print("[跳过] 未检测到环境变量 OPENAI_API_KEY，真实调用段不运行（未实跑）。")
        return
    try:
        agent = create_agent(
            "openai:gpt-4.1-mini",       # 示例模型名，请按官网当前列表替换
            tools=[],
            checkpointer=InMemorySaver(),  # 记忆保管员
        )
        config = {"configurable": {"thread_id": "user-001"}}  # 同一 id = 同一份记忆
        agent.invoke({"messages": [{"role": "user", "content": "我叫小明，请记住我"}]}, config)
        r = agent.invoke({"messages": [{"role": "user", "content": "我叫什么？"}]}, config)
        print("真实框架回复：", r["messages"][-1].content)
    except Exception as e:
        print(f"[提示] 真实调用失败：{e.__class__.__name__}——请检查 Key、网络与额度。")

if __name__ == "__main__":
    part1_offline()
    print()
    part2_real_framework()
