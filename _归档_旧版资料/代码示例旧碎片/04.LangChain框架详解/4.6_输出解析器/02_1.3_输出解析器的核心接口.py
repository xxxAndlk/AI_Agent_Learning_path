"""
BaseOutputParser接口详解
演示如何自定义输出解析器并理解核心接口
"""

from langchain_core.output_parsers import BaseOutputParser
from typing import List

# ============================================================
# 自定义输出解析器示例
# ============================================================
class NumberedListParser(BaseOutputParser[List[str]]):
    """
    解析编号列表的解析器
    将形如 "1. 项目一\n2. 项目二\n3. 项目三" 的文本
    转换为字符串列表
    """
    
    def parse(self, text: str) -> List[str]:
        """
        核心解析方法
        将原始文本解析为结构化对象
        """
        # 去除首尾空白
        text = text.strip()
        
        # 按行分割
        lines = text.split('\n')
        
        # 提取列表项
        result = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 移除可能的编号前缀（如 "1."、"2、"等）
            import re
            # 匹配编号模式：可选数字 + . 或 ) + 空格
            cleaned = re.sub(r'^\d+[.)]\s*', '', line)
            result.append(cleaned)
        
        return result
    
    @property
    def _type(self) -> str:
        """返回解析器类型标识"""
        return "numbered_list"

# 使用自定义解析器
parser = NumberedListParser()

# 测试解析
test_input = """
1. 第一项内容
2. 第二项内容
3. 第三项内容
"""

parsed_result = parser.parse(test_input)
print("解析结果：")
for i, item in enumerate(parsed_result, 1):
    print(f"{i}. {item}")

# 获取格式说明
format_instructions = parser.get_format_instructions()
print(f"\n格式说明: {format_instructions}")
