from langchain_core.tools import tool
from datetime import datetime, timedelta

@tool
def get_current_time(format: str = "iso") -> str:
    """获取当前时间
    
    Args:
        format: 时间格式，可选 "iso", "human", "timestamp"
        
    Returns:
        格式化后的时间字符串
    """
    now = datetime.now()
    
    if format == "iso":
        return now.isoformat()
    elif format == "human":
        return now.strftime("%Y年%m月%d日 %H:%M:%S")
    elif format == "timestamp":
        return str(int(now.timestamp()))
    else:
        return str(now)

@tool
def date_calculator(start_date: str, days: int, operation: str = "add") -> str:
    """日期计算器，可以加减天数
    
    Args:
        start_date: 起始日期，格式为 YYYY-MM-DD
        days: 要加减的天数
        operation: 操作类型，"add"加天数，"subtract"减天数
        
    Returns:
        计算后的日期
    """
    try:
        date = datetime.strptime(start_date, "%Y-%m-%d")
        
        if operation == "add":
            result = date + timedelta(days=days)
        elif operation == "subtract":
            result = date - timedelta(days=days)
        else:
            return f"无效的操作: {operation}"
        
        return result.strftime("%Y-%m-%d")
    except ValueError as e:
        return f"日期格式错误: {str(e)}"

# 测试工具
print(get_current_time.invoke({"format": "human"}))
print(date_calculator.invoke({"start_date": "2024-01-01", "days": 30, "operation": "add"}))
