from langchain_core.tools import tool
from typing import Optional
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
def robust_api_call(
    endpoint: str,
    method: str = "GET",
    retries: int = 3,
    timeout: int = 30
) -> str:
    """带重试机制的API调用
    
    Args:
        endpoint: API端点
        method: HTTP方法
        retries: 重试次数
        timeout: 超时时间
    """
    last_error = None
    
    for attempt in range(retries):
        try:
            logger.info(f"尝试调用API (尝试 {attempt + 1}/{retries})")
            
            # 模拟API调用
            if "error" in endpoint.lower():
                raise ConnectionError("模拟的连接错误")
            
            return f"成功调用 {endpoint}"
            
        except ConnectionError as e:
            last_error = e
            logger.warning(f"连接失败: {e}, 等待后重试...")
            time.sleep(2 ** attempt)  # 指数退避
            
        except TimeoutError as e:
            last_error = e
            logger.warning(f"请求超时: {e}")
            time.sleep(1)
            
        except Exception as e:
            last_error = e
            logger.error(f"未知错误: {e}")
            break
    
    return f"错误: 调用失败，已重试{retries}次 - {str(last_error)}"

# 测试错误处理
print(robust_api_call.invoke({"endpoint": "https://api.example.com"}))
print(robust_api_call.invoke({"endpoint": "https://error.example.com", "retries": 3}))
