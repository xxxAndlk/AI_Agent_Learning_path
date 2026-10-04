"""
LangChain基础链式调用示例
演示最基本的Prompt + LLM + Output Parser组合
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# ============================================================
# 步骤1：创建Chat模型实例
# ============================================================
# ChatOpenAI是LangChain对OpenAI Chat Completion API的封装
# model: 使用的模型名称，gpt-5.4-mini性价比高，gpt-5.4能力强
# temperature: 控制输出随机性，0.0最确定，1.0最随机
# streaming: 是否启用流式输出
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.7,
    streaming=True
)

# ============================================================
# 步骤2：定义Prompt模板
# ============================================================
# ChatPromptTemplate.from_messages() 用于定义多轮对话模板
# SystemMessage: 设定AI助手的行为和角色
# HumanMessage: 用户的输入，{topic}是模板变量
prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的技术文档撰写专家，擅长用通俗易懂的语言解释复杂概念。"),
    ("human", "请用3个要点解释什么是{topic}，每个要点不超过50字。")
])

# ============================================================
# 步骤3：创建输出解析器
# ============================================================
# StrOutputParser将模型的AIMessage输出转换为纯字符串
# 简化后续处理，不需要手动提取.content
output_parser = StrOutputParser()

# ============================================================
# 步骤4：使用LCEL组合链式调用
# ============================================================
# 管道操作符 | 用于组合组件，数据从左到右流动
# 执行顺序：输入 → prompt模板渲染 → LLM调用 → 输出解析
chain = prompt | llm | output_parser

# ============================================================
# 步骤5：执行链式调用（同步）
# ============================================================
# invoke()方法接收字典作为输入，对应模板中的变量
# {"topic": "机器学习"} 会填充模板中的{topic}占位符
result = chain.invoke({"topic": "机器学习"})
print("同步调用结果：")
print(result)

# ============================================================
# 步骤6：流式输出（实时显示）
# ============================================================
# stream()方法返回生成器，可以逐token获取输出
# 适合UI实时显示，提升用户体验
print("\n流式输出：")
for chunk in chain.stream({"topic": "深度学习"}):
    # chunk是字符串片段，直接打印不换行实现打字机效果
    print(chunk, end="", flush=True)
print()

# ============================================================
# 步骤7：批处理（批量调用）
# ============================================================
# batch()方法接收输入列表，并行处理多个请求
# 内部自动管理并发，提高效率
inputs = [
    {"topic": "区块链"},
    {"topic": "云计算"},
    {"topic": "物联网"}
]
results = chain.batch(inputs)
print("\n批处理结果：")
for i, result in enumerate(results, 1):
    print(f"{i}. {result[:100]}...")
