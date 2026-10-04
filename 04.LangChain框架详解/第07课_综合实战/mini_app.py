# -*- coding: utf-8 -*-
# 用途：第07课《综合实战》配套演示——把检索、记忆、工具、模型组装成一个最小可跑的小应用。
#       第①段纯标准库、离线真跑（假向量检索 + 拼提示 + 白名单计算器/报时工具）；
#       第②段装了 langchain 即可离线跑（InMemoryVectorStore + 提示模板 + @tool）；
#       第③段模型调用需 API Key：需 API Key，未实跑，配置后可自行运行，不伪造输出。
# pip install langchain langchain-openai langchain-core python-dotenv
# 运行前配置环境变量 OPENAI_API_KEY（或在本文件同目录建 .env 写 OPENAI_API_KEY=sk-...，
# .env 不要提交到代码仓库）。

import ast
import math
import os
import time

# 可选：装了 python-dotenv 就从 .env 读 Key；没装也不影响
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


# ============================================================ 三段共用：小资料与工具逻辑
# 资料直接写死在代码里：不依赖外部文件，任何机器都能跑。真项目里它们来自文档切块入库。
DOCS = [
    "LangChain 把大模型应用里反复出现的零件都做好了，LCEL 是它拼装零件的管道写法。",
    "LCEL 用竖线把零件串成链：提示模板接模型，模型接输出解析器，字典汇合各路输入。",
    "记忆的主流做法是 checkpointer 配 thread_id：同一段对话共用一个线程号，历史自动带回。",
    "检索器的约定：一个字符串进去，一列最相关的 Document 出来。",
    "工具用 @tool 定义：函数加说明加类型标注，就成了模型看得懂的说明书。",
]

# 锚点词：数一数每条资料里出现几次，凑成一个"手工向量"。
# 真项目这一步由嵌入模型完成，效果远好于数词，但"把文本变成向量"这件事是同一件。
ANCHORS = ["LangChain", "LCEL", "记忆", "checkpointer", "检索", "Document", "工具", "@tool"]


def hand_embed(text: str) -> list:
    return [text.count(a) for a in ANCHORS]


def cosine(a: list, b: list) -> float:
    da = math.sqrt(sum(x * x for x in a))
    db = math.sqrt(sum(x * x for x in b))
    if da == 0 or db == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (da * db)


def retrieve(question: str, k: int = 2) -> list:
    """算相似度、排序、取前 k 条——向量检索的手动挡核心就这三步。"""
    q = hand_embed(question)
    scored = sorted(((cosine(q, hand_embed(d)), d) for d in DOCS),
                    key=lambda pair: pair[0], reverse=True)
    return scored[:k]


def build_prompt(question: str, docs: list) -> str:
    """把检索结果格式化成列表，和问题一起装进固定句式——提示装配的手动挡。"""
    context = "\n".join(f"- {text}" for _, text in docs)
    return (
        "仅根据以下资料回答问题，资料里没有就直说不知道。\n\n"
        f"资料：\n{context}\n\n问题：{question}"
    )


def safe_calc(expression: str) -> str:
    """只放行数字与 + - * / 的计算器。绝不直接 eval 模型给的字符串——
    那等于把家门钥匙交给陌生人（一句 __import__('os') 就能搬空你家）。
    ast 白名单像小区门禁：登记过的住户（数字、四则节点）能进，生面孔一律挡下。"""
    ALLOWED = (ast.Expression, ast.BinOp, ast.UnaryOp, ast.Constant,
               ast.Add, ast.Sub, ast.Mult, ast.Div, ast.USub, ast.UAdd)
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError:
        return "表达式看不懂，检查一下写法？"
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant):
            if not isinstance(node.value, (int, float)):  # 字符串常量也不放行，防 'hi'*3
                return "只支持数字和 + - * /。"
        elif not isinstance(node, ALLOWED):
            return "只支持数字和 + - * /，不支持别的玩法。"
    try:
        # 连内置函数都清空，算术不再需要任何"外援"
        return str(eval(compile(tree, "<calc>", "eval"), {"__builtins__": {}}, {}))
    except ZeroDivisionError:
        return "除数不能是 0。"


def now_time(_: str = "") -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def build_tools():
    """两个纯标准库实现的工具。工具逻辑永远是你自己的 Python，
    框架（@tool）只负责把说明书递给模型、把模型的决定递回给你。"""
    from langchain_core.tools import tool

    @tool
    def now_time_tool(_: str = "") -> str:
        """返回当前的日期和时间。需要知道现在几点时调用。"""
        return now_time()

    @tool
    def calc_tool(expression: str) -> str:
        """计算一个只含数字与 + - * / 的算式。需要精确计算时调用。"""
        return safe_calc(expression)

    return [now_time_tool, calc_tool]


# ============================================================ 第①段：离线真跑（不需要框架和 Key）
def offline_demo() -> None:
    print("== 第①段：离线真跑（纯标准库，不需要框架和 Key）==")
    question = "LCEL 怎么把零件串起来？"
    docs = retrieve(question, k=2)
    print(f"问题：{question}")
    print("检索结果（假向量 + 余弦相似度）：")
    for score, text in docs:
        print(f"  相似度 {score:.3f}  {text}")

    print("\n拼好的提示长这样：")
    print("-" * 46)
    print(build_prompt(question, docs))
    print("-" * 46)

    print("\n顺手试一下两个工具：")
    print("safe_calc('12 * 3 + 4')       ->", safe_calc("12 * 3 + 4"))
    print("safe_calc('__import__(\"os\")') ->", safe_calc('__import__("os")'), "（门禁挡下了）")
    print("now_time()                    ->", now_time(), "（当前时间）\n")


# ============================================================ 第②段：LangChain 组装（离线可跑）
def build_retriever():
    """把第一段的假向量插进框架的 Embeddings 插座，换来一个标准检索器。"""
    from langchain_core.documents import Document
    from langchain_core.embeddings import Embeddings
    from langchain_core.vectorstores import InMemoryVectorStore

    class HandEmbeddings(Embeddings):
        """接口对上（embed_documents / embed_query），土向量仪就能在框架里冒充真货；
        以后换 OpenAIEmbeddings 只改这一处，插头一样，电器随便换。"""

        def embed_documents(self, texts):
            return [hand_embed(t) for t in texts]

        def embed_query(self, text):
            return hand_embed(text)

    store = InMemoryVectorStore(HandEmbeddings())
    store.add_documents([Document(page_content=t, metadata={"source": f"资料{i + 1}"})
                         for i, t in enumerate(DOCS)])
    return store.as_retriever(search_kwargs={"k": 2})


def langchain_demo() -> None:
    print("== 第②段：同样的零件换上 LangChain 的外壳（离线可跑，不需要 Key）==")
    try:
        from langchain_core.messages import AIMessage, HumanMessage
        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        retriever = build_retriever()
    except ImportError as e:
        print(f"（还没装 langchain，跳过这段：{e}）")
        print("（安装：pip install langchain langchain-openai langchain-core）\n")
        return

    hits = retriever.invoke("检索器和 Document 的约定是什么？")
    print("检索器捞上来的资料：")
    for d in hits:
        print(f"  [{d.metadata['source']}] {d.page_content}")

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是资料问答助手，仅根据资料回答，资料里没有就直说不知道。"),
        MessagesPlaceholder("history", optional=True),  # 多轮记忆在这里占座
        ("human", "资料：\n{context}\n\n问题：{question}"),
    ])
    filled = prompt.invoke({
        "context": "（这里会是检索捞到的资料）",
        "question": "你还记得我叫什么吗？",
        "history": [HumanMessage("我叫小林"), AIMessage("你好，小林！")],  # 手动塞两条假历史
    })
    print("\n模板渲染结果（中间两条就是记忆占位被填上的样子）：")
    for m in filled.messages:
        print(f"  [{m.type}] {m.content}")

    print("\n@tool 自动生成的工具说明书：")
    for t in build_tools():
        print(f"  {t.name}：{t.description}")
    print()


# ============================================================ 第③段：模型调用（需 API Key，未实跑）
def online_demo() -> None:
    print("== 第③段：通电——模型调用（需 API Key，未实跑）==")
    if not os.environ.get("OPENAI_API_KEY"):
        print("（没检测到 OPENAI_API_KEY，跳过。配置后重新运行即可看到真实输出；")
        print("  该段会产生少量费用，本课写作时未实跑，不伪造输出。）\n")
        return
    try:
        from langchain.agents import create_agent
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.runnables import RunnablePassthrough
        from langchain_openai import ChatOpenAI
        from langgraph.checkpoint.memory import InMemorySaver

        retriever = build_retriever()
    except ImportError as e:
        print(f"（依赖没装齐，跳过：{e}）")
        print("（安装：pip install langchain langchain-openai）\n")
        return

    model = ChatOpenAI(model="gpt-4o-mini")  # 示例名，实际按官网模型列表选当前便宜够用的

    def format_docs(docs):
        return "\n".join(f"- {d.page_content}" for d in docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "你是资料问答助手，仅根据资料回答，资料里没有就直说不知道。"),
        ("human", "资料：\n{context}\n\n问题：{question}"),
    ])
    rag_chain = (
        {"context": retriever | format_docs,   # 这一灶：问题 -> 资料
         "question": RunnablePassthrough()}    # 这一灶：问题原样通过
        | prompt
        | model
        | StrOutputParser()
    )

    print("跑法一：固定链（检索 + LCEL + 输出解析）")
    print("LCEL 怎么把零件串起来？")
    print(rag_chain.invoke("LCEL 怎么把零件串起来？"))

    print("\n跑法二：Agent（自主选工具 + checkpointer 多轮记忆）")
    agent = create_agent(
        model=model,
        tools=build_tools(),
        system_prompt="你是资料问答助手，回答简短；资料之外的问题可以调用工具或直说不知道。",
        checkpointer=InMemorySaver(),  # 存内存：程序重启就没了；跨重启换 SQLite 等实现
    )
    config = {"configurable": {"thread_id": "chat-1"}}  # 同一段对话共用一个线程号

    r1 = agent.invoke({"messages": [{"role": "user", "content": "帮我算一下 12 * 3 + 4"}]}, config)
    print("第1轮：", r1["messages"][-1].content)
    r2 = agent.invoke({"messages": [{"role": "user", "content": "谢谢！再报一下现在的时间"}]}, config)
    print("第2轮：", r2["messages"][-1].content)
    print("-> 第2轮能接着聊，说明同一 thread_id 的历史被自动带上了。\n")


def main() -> None:
    print("第 07 课综合实战 mini_app：检索 + 记忆 + 工具 + 模型\n")
    offline_demo()
    langchain_demo()
    online_demo()


if __name__ == "__main__":
    main()
