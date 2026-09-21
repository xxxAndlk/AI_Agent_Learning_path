from langchain_core.tools import tool
from typing import List
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

# 工具1: 数据获取
@tool
def fetch_stock_data(symbol: str, days: int = 7) -> str:
    """获取股票数据
    
    Args:
        symbol: 股票代码
        days: 查询天数
    """
    return f"{symbol} 最近{days}天的股票数据: 开盘价100, 收盘价105"

# 工具2: 数据分析
@tool
def analyze_data(data: str, analysis_type: str = "basic") -> str:
    """分析数据
    
    Args:
        data: 要分析的数据
        analysis_type: 分析类型 basic/advanced
    """
    if analysis_type == "basic":
        return f"基础分析结果: 上涨趋势, 波动较小"
    return f"高级分析结果: 技术指标显示买入信号"

# 工具3: 生成报告
@tool
def generate_report(stock_data: str, analysis: str) -> str:
    """生成分析报告
    
    Args:
        stock_data: 股票数据
        analysis: 分析结果
    """
    return f"""
========== 股票分析报告 ==========
{stock_data}

{analysis}
==================================
报告生成完成
"""

# 创建Agent（v1.x 推荐方式）
llm = ChatOpenAI(model="gpt-5.4")
tools = [fetch_stock_data, analyze_data, generate_report]

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""你是一个股票分析助手。
    
工作流程:
1. 首先获取股票数据
2. 然后分析数据
3. 最后生成报告

请按照这个流程来处理用户的请求。
"""
)

# 执行多工具协作任务
result = agent.invoke({
    "input": "分析苹果公司(AAPL)最近30天的股票走势"
})
print(result["messages"][-1].content)
