"""
构建复杂链的示例
展示并行、条件和动态链的构建方法
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import (
    RunnableParallel,
    RunnableBranch,
    RunnablePassthrough,
    RunnableLambda
)
import json

llm = ChatOpenAI()

# ============================================================
# 复杂链1：多角度分析链
# ============================================================

# 同时从多个角度分析同一个问题
analysis_perspectives = {
    "technical": (
        ChatPromptTemplate.from_template("从技术角度分析：{topic}")
        | llm | StrOutputParser()
    ),
    "business": (
        ChatPromptTemplate.from_template("从商业角度分析：{topic}")
        | llm | StrOutputParser()
    ),
    "ethical": (
        ChatPromptTemplate.from_template("从伦理角度分析：{topic}")
        | llm | StrOutputParser()
    )
}

multi_analysis = RunnableParallel(**analysis_perspectives)

result = multi_analysis.invoke({"topic": "人工智能"})
print("技术角度:", result["technical"][:50])
print("商业角度:", result["business"][:50])
print("伦理角度:", result["ethical"][:50])

# ============================================================
# 复杂链2：带条件判断的链
# ============================================================

def needs_citation(question: str) -> bool:
    """判断问题是否需要引用来源"""
    return any(kw in question for kw in ["根据", "研究表明", "数据显示"])

def needs_steps(question: str) -> bool:
    """判断问题是否需要步骤说明"""
    return any(kw in question for kw in ["如何", "怎么", "步骤"])

# 不同的处理链
with_citation_chain = (
    ChatPromptTemplate.from_template("回答并引用可靠来源：{question}")
    | llm | StrOutputParser()
)

with_steps_chain = (
    ChatPromptTemplate.from_template("分步骤详细回答：{question}")
    | llm | StrOutputParser()
)

general_chain = (
    ChatPromptTemplate.from_template("简明扼要地回答：{question}")
    | llm | StrOutputParser()
)

# 构建条件链
conditional_chain = RunnableBranch(
    (lambda x: needs_citation(x["question"]), with_citation_chain),
    (lambda x: needs_steps(x["question"]), with_steps_chain),
    general_chain
)

# 测试不同的输入
result1 = conditional_chain.invoke({"question": "如何学习Python？"})
result2 = conditional_chain.invoke({"question": "根据研究，最有效的学习方法是什么？"})
print(f"需要步骤的问题: {result1[:50]}...")
print(f"需要引用的问题: {result2[:50]}...")

# ============================================================
# 复杂链3：动态构建的链
# ============================================================

def create_dynamic_chain(template_type: str):
    """根据参数动态创建不同的链"""
    
    templates = {
        "formal": "用正式的语气回答：{question}",
        "casual": "用轻松友好的语气回答：{question}",
        "technical": "用专业技术的语言回答：{question}"
    }
    
    prompt = ChatPromptTemplate.from_template(
        templates.get(template_type, templates["formal"])
    )
    
    return prompt | llm | StrOutputParser()

# 运行时动态选择
chain_formal = create_dynamic_chain("formal")
chain_casual = create_dynamic_chain("casual")

result1 = chain_formal.invoke({"question": "什么是API？"})
result2 = chain_casual.invoke({"question": "什么是API？"})
print(f"正式风格: {result1}")
print(f"轻松风格: {result2}")
