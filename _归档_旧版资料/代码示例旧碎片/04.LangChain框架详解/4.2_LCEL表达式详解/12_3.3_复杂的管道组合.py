"""
复杂的管道组合示例
展示分支、合并、条件等高级模式
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableBranch, RunnablePassthrough
from langchain_core.runnables import RunnableLambda

llm = ChatOpenAI()

# ============================================================
# 模式1：并行处理 + 结果合并
# ============================================================

# 同时生成不同风格的回复
formal_prompt = ChatPromptTemplate.from_template("用正式的语气回答：{question}")
casual_prompt = ChatPromptTemplate.from_template("用轻松的语气回答：{question}")
technical_prompt = ChatPromptTemplate.from_template("用专业的技术语言回答：{question}")

# 构建并行链
multi_style_chain = RunnableParallel(
    formal=formal_prompt | llm | StrOutputParser(),
    casual=casual_prompt | llm | StrOutputParser(),
    technical=technical_prompt | llm | StrOutputParser()
)

result = multi_style_chain.invoke({"question": "什么是机器学习"})
print(f"正式风格: {result['formal'][:50]}...")
print(f"轻松风格: {result['casual'][:50]}...")
print(f"技术风格: {result['technical'][:50]}...")

# ============================================================
# 模式2：条件分支
# ============================================================

# 根据问题类型选择不同的处理链
def classify_question(question: str) -> str:
    """简单的规则判断问题类型"""
    if "如何" in question or "怎么" in question:
        return "howto"
    elif "什么" in question or "什么是" in question:
        return "definition"
    else:
        return "general"

# 定义不同类型的处理链
howto_chain = (
    ChatPromptTemplate.from_template("提供详细的步骤指南：{question}")
    | llm | StrOutputParser()
)

definition_chain = (
    ChatPromptTemplate.from_template("给出清晰的定义和例子：{question}")
    | llm | StrOutputParser()
)

general_chain = (
    ChatPromptTemplate.from_template("简洁地回答：{question}")
    | llm | StrOutputParser()
)

# 使用RunnableBranch实现条件分支
# 第一个参数是条件函数，返回True时选择对应的分支
branch_chain = RunnableBranch(
    (lambda x: "如何" in x["question"] or "怎么" in x["question"], howto_chain),
    (lambda x: "什么" in x["question"], definition_chain),
    general_chain  # 默认分支
)

result = branch_chain.invoke({"question": "如何学习Python"})
print(f"条件分支结果: {result[:100]}...")
