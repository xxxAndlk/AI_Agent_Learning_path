from langchain.agents import load_tools
from langchain_openai import ChatOpenAI

# 初始化LLM
llm = ChatOpenAI(model="gpt-5.4")

# 加载多个工具
# 注意：某些工具需要API密钥
tool_names = ["serpapi", "wikipedia", "pal-math", "requests"]
tools = load_tools(tool_names, llm=llm)

# 创建工具字典便于查找
tools_dict = {tool.name: tool for tool in tools}

# 手动调用工具
if "wikipedia" in tools_dict:
    wiki_result = tools_dict["wikipedia"].invoke("人工智能")
    print(wiki_result)
