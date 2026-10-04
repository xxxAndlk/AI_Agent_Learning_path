"""
深入理解管道操作符的实现原理
"""

from langchain_core.runnables import Runnable, RunnableLambda
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI()

# ============================================================
# 管道操作符的内部实现
# ============================================================

# 当我们写 prompt | llm 时，实际调用的是：
# prompt.__or__(llm) 或 llm.__ror__(prompt)

# 这个方法返回一个RunnableSequence对象
# 内部包含两个重要的函数：
# 1. first: 第一个Runnable，接收原始输入
# 2. last: 后续的Runnable，接收前一步的输出

# 例如：prompt | llm 等价于：
chain = RunnableLambda(
    lambda x: llm.invoke(prompt.invoke(x))
).bind()  # 这是一个简化的等价表达

# 实际使用时，LCEL的处理更加复杂：
# - 自动处理字典到单值的转换
# - 自动处理不同输出类型的适配
# - 支持并行执行优化

# ============================================================
# 管道操作符的类型传递
# ============================================================

# LCEL的一个重要特性是类型推断
# 让我们看看输入输出类型是如何传递的

prompt = ChatPromptTemplate.from_template("{text}")
# prompt的输入类型: Dict[str, Any]
# prompt的输出类型: BaseMessage

chain1 = prompt | llm
# chain1的输入类型: Dict[str, Any]
# chain1的输出类型: AIMessage

chain2 = chain1 | StrOutputParser()
# chain2的输入类型: Dict[str, Any]
# chain2的输出类型: str

# 类型信息对于静态检查和IDE自动补全非常重要
# 可以通过chain.input_schema和chain.output_schema查看
print(f"输入模式: {chain2.input_schema}")
print(f"输出模式: {chain2.output_schema}")
