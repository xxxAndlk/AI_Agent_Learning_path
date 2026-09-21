"""
错误处理最佳实践
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser, OutputFixingParser
from typing import Optional

# ============================================================
# 错误处理模式
# ============================================================

class SafeJsonParser:
    """
    安全的JSON解析器
    包含完善的错误处理逻辑
    """
    
    def __init__(self, max_retries: int = 3):
        self.parser = JsonOutputParser()
        self.llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
        self.fixer = OutputFixingParser(
            parser=self.parser,
            llm=self.llm,
            max_retries=max_retries
        )
    
    def parse(self, text: str) -> Optional[dict]:
        """安全地解析JSON，处理各种错误"""
        # 策略1：直接解析
        try:
            return self.parser.parse(text)
        except Exception as e:
            print(f"直接解析失败: {e}")
        
        # 策略2：尝试修复
        try:
            return self.fixer.parse(text)
        except Exception as e:
            print(f"修复解析失败: {e}")
        
        # 策略3：返回None或默认值
        return None
    
    def parse_with_fallback(self, text: str, fallback: dict = None) -> dict:
        """带默认值的解析"""
        result = self.parse(text)
        return result if result is not None else (fallback or {})

# 使用示例
safe_parser = SafeJsonParser()

# 测试有问题的输入
bad_json = "这是一些无关文本，没有任何JSON"

result = safe_parser.parse_with_fallback(bad_json, fallback={"error": "解析失败"})
print(f"解析结果: {result}")
