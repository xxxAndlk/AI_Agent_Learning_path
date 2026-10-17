# 用途：第01课《LangChain是什么》最小示例——提示模板接模型，用 .invoke 跑通第一条链。
# pip install langchain langchain-openai python-dotenv（langchain-openai 借 OpenAI 兼容协议接 DeepSeek）
# 注意：调模型需要 DEEPSEEK_API_KEY（从环境变量或 .env 读取）；联网调用部分需 Key，未实跑，不伪造输出。

import os
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()  # 从同目录 .env 读取配置；没有这个文件也不报错
except ImportError:
    pass  # 没装 python-dotenv 就直接用系统环境变量，不影响运行


def main() -> None:
    # 先查 Key 再碰依赖：没配 Key 时不用装 langchain 也能得到清晰的中文指引
    if not os.environ.get("DEEPSEEK_API_KEY"):
        print("没找到 DEEPSEEK_API_KEY，本演示需联网调用 DeepSeek，已跳过。")
        print("配置方法（三选一）：")
        print('  1) PowerShell 执行 $env:DEEPSEEK_API_KEY="sk-..."（当前窗口生效）')
        print("  2) macOS/Linux 在 ~/.zshrc 或 ~/.bashrc 里加 export DEEPSEEK_API_KEY=你的key")
        print("  3) 在本文件同目录建 .env 文件，写入一行：DEEPSEEK_API_KEY=你的key（勿提交 git）")
        return

    try:
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_openai import ChatOpenAI
    except ImportError:
        print("依赖还没装好，请先执行：pip install langchain langchain-openai python-dotenv")
        sys.exit(1)

    # 模板管"话怎么说"，模型管"话谁来说"，竖线把它们串成一条链
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "你是一个说话简洁的编程老师。"),
            ("human", "用一句话解释什么是{thing}。"),
        ]
    )
    model = ChatOpenAI(
        model=os.environ.get("DEEPSEEK_MODEL", "deepseek-flash"),  # 示例名可能更新，以 DeepSeek 官网模型列表为准
        api_key=os.environ.get("DEEPSEEK_API_KEY"),
        base_url="https://api.deepseek.com",  # langchain-openai 借 OpenAI 兼容协议接 DeepSeek
    )

    chain = prompt | model

    try:
        response = chain.invoke({"thing": "LangChain"})
        print(response.content)
    except Exception as exc:  # 网络不通、额度用尽、key 不对等问题都在这里兜住
        print(f"调用模型失败了：{exc}")
        print("常见原因：key 填错、网络不通、账户额度用尽。排查后再试一次。")
        sys.exit(1)


if __name__ == "__main__":
    main()
