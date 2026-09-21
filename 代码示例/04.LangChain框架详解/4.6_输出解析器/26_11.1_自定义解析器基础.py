"""
自定义输出解析器基础
展示如何创建自定义解析器
"""

from langchain_core.output_parsers import BaseOutputParser
from typing import List, Dict, Any

# ============================================================
# 自定义解析器示例：键值对解析器
# ============================================================
class KeyValueParser(BaseOutputParser[Dict[str, str]]):
    """
    键值对解析器
    解析形如 "key1=value1\nkey2=value2" 的文本
    返回字典
    """
    
    def parse(self, text: str) -> Dict[str, str]:
        """解析键值对文本"""
        result = {}
        
        # 按行分割
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试分割键值对
            if '=' in line:
                key, value = line.split('=', 1)
                result[key.strip()] = value.strip()
            elif ':' in line:
                key, value = line.split(':', 1)
                result[key.strip()] = value.strip()
        
        return result
    
    @property
    def _type(self) -> str:
        return "key_value"

# ============================================================
# 使用自定义解析器
# ============================================================
parser = KeyValueParser()

test_input = """
username = zhangsan
email = zhangsan@example.com
phone: 13800138000
address: 北京市朝阳区
"""

result = parser.parse(test_input)
print("解析结果：")
for key, value in result.items():
    print(f"  {key}: {value}")

print(f"\n类型: {type(result)}")
