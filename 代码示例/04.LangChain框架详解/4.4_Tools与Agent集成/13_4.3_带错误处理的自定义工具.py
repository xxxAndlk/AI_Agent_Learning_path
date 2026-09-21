from langchain_core.tools import tool
from typing import Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def call_external_api(
    endpoint: str,
    method: str = "GET",
    data: Optional[dict] = None,
    timeout: int = 30
) -> str:
    """调用外部API
    
    Args:
        endpoint: API端点URL
        method: HTTP方法 GET/POST/PUT/DELETE
        data: 请求数据（用于POST/PUT）
        timeout: 超时时间（秒）
        
    Returns:
        API响应结果
    """
    # 错误处理示例
    if timeout <= 0 or timeout > 60:
        return "错误: 超时时间必须在1-60秒之间"
    
    if method not in ["GET", "POST", "PUT", "DELETE"]:
        return f"错误: 不支持的HTTP方法 {method}"
    
    try:
        # 实际实现中这里调用API
        # import requests
        # response = requests.request(method, endpoint, json=data, timeout=timeout)
        # return response.text
        
        # 模拟成功响应
        return f"成功调用 {endpoint}，方法: {method}"
        
    except Exception as e:
        logger.error(f"API调用失败: {str(e)}")
        return f"错误: API调用失败 - {str(e)}"

# 测试错误处理
print(call_external_api.invoke({"endpoint": "https://api.example.com", "timeout": 0}))
print(call_external_api.invoke({"endpoint": "https://api.example.com", "method": "INVALID"}))
