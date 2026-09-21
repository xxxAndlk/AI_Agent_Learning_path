from langchain.agents import load_tools
from langchain_openai import ChatOpenAI

# 加载内置工具
llm = ChatOpenAI(model="gpt-5.4")
tools = load_tools(["pal-math"], llm=llm)

# pal-math是一个数学推理工具，擅长复杂数学问题
math_tool = tools[0]
result = math_tool.invoke("如果一个水池每小时进水50升，同时每小时出水30升，8小时后水池中有多少水？")
print(result)
