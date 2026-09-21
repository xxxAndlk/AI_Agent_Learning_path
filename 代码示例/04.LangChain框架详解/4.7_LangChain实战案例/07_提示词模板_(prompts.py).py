"""
提示词模板模块
预定义各种场景的提示词模板
"""
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

# 通用问答提示词
QA_SYSTEM_PROMPT = """你是一个专业的知识库问答助手。
请根据提供的上下文信息回答用户的问题。
如果上下文中没有相关信息，请明确告知用户你无法从知识库中找到答案。
请用清晰、准确的中文回答问题。"""

# 带引用来源的提示词
QA_WITH_SOURCE_PROMPT = """你是一个专业的知识库问答助手。
请根据提供的上下文信息回答用户的问题。

要求：
1. 只使用提供的上下文信息回答，不要添加外部知识
2. 如果无法从上下文找到答案，明确告知用户
3. 在回答中注明信息来源
4. 用清晰、准确的中文回答"""

# 总结摘要提示词
SUMMARY_PROMPT = """请根据以下文档内容生成简洁的摘要：

{context}

要求：
1. 提取关键信息
2. 保持原文的核心含义
3. 摘要长度控制在 200 字以内"""

# 对比分析提示词
COMPARISON_PROMPT = """请对比分析以下两个文档的异同：

文档 A:
{doc_a}

文档 B:
{doc_b}

请从以下几个方面进行分析：
1. 相同点
2. 不同点
3. 各自的优势和劣势"""

# 代码解释提示词
CODE_EXPLANATION_PROMPT = """请解释以下代码的功能和工作原理：

```{language}
{code}
```

请提供：
1. 代码整体功能描述
2. 关键部分的详细说明
3. 可能的改进建议"""


def get_qa_prompt(system_prompt: str = QA_SYSTEM_PROMPT) -> ChatPromptTemplate:
    """获取问答提示词模板"""
    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "上下文信息:\n{context}\n\n用户问题: {question}"),
    ])


def get_summary_prompt() -> PromptTemplate:
    """获取摘要提示词模板"""
    return PromptTemplate(
        template=SUMMARY_PROMPT,
        input_variables=["context"],
    )


def get_comparison_prompt() -> PromptTemplate:
    """获取对比分析提示词模板"""
    return PromptTemplate(
        template=COMPARISON_PROMPT,
        input_variables=["doc_a", "doc_b"],
    )


def get_code_explanation_prompt() -> PromptTemplate:
    """获取代码解释提示词模板"""
    return PromptTemplate(
        template=CODE_EXPLANATION_PROMPT,
        input_variables=["language", "code"],
    )
