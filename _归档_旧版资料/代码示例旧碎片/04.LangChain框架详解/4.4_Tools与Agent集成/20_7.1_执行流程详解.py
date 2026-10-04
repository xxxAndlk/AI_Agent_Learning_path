from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# 定义工具
@tool
def search_products(query: str, category: str = "all", max_results: int = 5) -> str:
    """搜索产品
    
    Args:
        query: 搜索关键词
        category: 产品类别
        max_results: 最大结果数
    """
    # 模拟产品数据
    products = [
        {"name": "iPhone 15", "price": 6999, "category": "手机"},
        {"name": "MacBook Pro", "price": 12999, "category": "电脑"},
        {"name": "AirPods Pro", "price": 1999, "category": "耳机"}
    ]
    
    results = []
    for p in products[:max_results]:
        if category == "all" or p["category"] == category:
            results.append(f"{p['name']} - ¥{p['price']}")
    
    return "\n".join(results) if results else "未找到产品"

# 创建Agent（v1.x 推荐方式）
llm = ChatOpenAI(model="gpt-5.4")
tools = [search_products]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个智能助手，帮助用户搜索产品信息。"
)

# 执行
result = agent.invoke({
    "input": "帮我搜索价格在5000元以上的产品，最多返回3个"
})
print(result["messages"][-1].content)
