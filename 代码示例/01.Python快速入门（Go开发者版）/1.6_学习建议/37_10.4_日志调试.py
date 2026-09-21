import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def process_request(data: dict):
    """处理请求的函数"""
    logger.debug(f"收到数据: {data}")
    
    try:
        result = transform_data(data)
        logger.info(f"处理成功: {result}")
        return result
    except Exception as e:
        logger.error(f"处理失败: {e}", exc_info=True)  # exc_info=True 打印完整追溯
        raise

# 条件日志（避免生产环境性能开销）
import logging

# 使用日志而不是 print，因为可以控制级别
logger = logging.getLogger(__name__)

# 调试时：
# export LOG_LEVEL=DEBUG  # Linux/Mac
# set LOG_LEVEL=DEBUG     # Windows

level = os.environ.get('LOG_LEVEL', 'INFO')
logger.setLevel(getattr(logging, level))

import os
