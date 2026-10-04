# -*- coding: utf-8 -*-
# 用途：LCEL 管道演示——顺序链、并行链、重试与兜底，外加一条不联网的纯 Runnable 小链。
# 安装：pip install langchain langchain-openai python-dotenv
# 说明：联网调用大模型需要 API Key，本文件未实跑、仅演示写法；
#       没填 Key 时也能先跑离线小链，感受管道的用法。

import os

# 可选：把项目目录下 .env 里的配置读进环境变量（.env 不要提交到 git）
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough


def build_model():
    """模型名从环境变量读，没设就用示例名（可能已更新，按官网模型列表选便宜够用的）。"""
    from langchain_openai import ChatOpenAI

    return ChatOpenAI(model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))


def offline_demo():
    """不依赖大模型：纯 Runnable 拼链，装了 langchain 就能真跑。"""
    # 一条最简单的数值流水线：翻倍 -> 加一。上一步的产出自动成为下一步的输入。
    pipe = RunnableLambda(lambda x: x * 2) | RunnableLambda(lambda x: x + 1)
    print("离线顺序链 3 ->", pipe.invoke(3))  # 7

    # 并行：同一份输入同时送进两个分支，结果按 key 汇合回字典。
    both = RunnableParallel(
        kept=RunnablePassthrough(),  # 原样透传
        shout=RunnableLambda(lambda s: str(s).upper()),  # 小函数做转接
    )
    print("离线并行 'hi' ->", both.invoke("hi"))  # {'kept': 'hi', 'shout': 'HI'}


def online_demo():
    """联网部分：需要 OPENAI_API_KEY，会产生少量费用。"""
    model = build_model()

    # ① 顺序链：提示 | 模型 | 字符串输出，最经典的一条。
    basic_chain = (
        ChatPromptTemplate.from_template("用一句话给零基础读者解释：{question}")
        | model
        | StrOutputParser()
    )

    # ② 并行链：同一个问题，一边生成回答、一边起标题，按 key 汇合。
    parallel = RunnableParallel(
        answer=basic_chain,
        title=(
            ChatPromptTemplate.from_template("给问题「{question}」起一个10字以内的标题")
            | model
            | StrOutputParser()
        ),
    )
    result = parallel.invoke({"question": "什么是向量数据库"})
    print("回答：", result["answer"])
    print("标题：", result["title"])

    # ③ 重试 + 兜底：先自动重拨 3 次，仍失败就切备用。
    safe_chain = (
        basic_chain.with_retry(stop_after_attempt=3)
        # 备用这里用假回答示意结构；真实项目里换成另一个模型实例，
        # 比如 backup = build_model()（换个 model 名）后 with_fallbacks([backup])。
        .with_fallbacks([RunnableLambda(lambda _: "（备用回答：主模型暂时不可用）")])
    )
    print("兜底链回答：", safe_chain.invoke({"question": "什么是微调"}))


def main():
    print("== 离线小链（不需要 API Key）==")
    try:
        offline_demo()
    except Exception as exc:  # 没装 langchain 也会走到这里
        print(f"离线部分没法跑：{exc}")
        print("多半是还没装依赖，先执行：pip install langchain")
        return

    if not os.environ.get("OPENAI_API_KEY"):
        print("\n提示：没设置 OPENAI_API_KEY，联网演示已跳过。")
        print("Windows：setx OPENAI_API_KEY 你的key（重开终端生效）")
        print("macOS/Linux：在 ~/.zshrc 或 ~/.bashrc 里加 export OPENAI_API_KEY=你的key")
        return

    print("\n== 联网链路（需要 API Key）==")
    try:
        online_demo()
    except Exception:
        print("联网调用失败了。常见原因：Key 不对、网络不通、账户额度用完，")
        print("逐项检查后重试；真实项目里应把错误记进日志并给用户友好提示。")


if __name__ == "__main__":
    main()
