"""
日程提取器实现
使用DatetimeOutputParser从文本中提取日程信息
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import DatetimeOutputParser
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# ============================================================
# 定义日程数据模型
# ============================================================
class ScheduleEvent(BaseModel):
    """日程事件模型"""
    title: str = Field(description="事件标题")
    start_time: datetime = Field(description="开始时间")
    end_time: Optional[datetime] = Field(default=None, description="结束时间")
    location: Optional[str] = Field(default=None, description="地点")
    description: Optional[str] = Field(default=None, description="描述")

# ============================================================
# 日程提取器实现
# ============================================================
from langchain_core.output_parsers import JsonOutputParser

class ScheduleExtractor:
    """日程信息提取器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
        
        # 解析时间
        self.time_parser = DatetimeOutputParser()
        
        # 解析JSON
        self.json_parser = JsonOutputParser(pydantic_object=ScheduleEvent)
    
    def extract(self, text: str) -> ScheduleEvent:
        """从文本中提取日程信息"""
        
        # 构建提示词
        prompt = ChatPromptTemplate.from_template(
            "从以下文本中提取日程信息，转换为JSON格式。"
            "时间使用ISO 8601格式（如2024-03-15T15:00:00）。\n\n"
            "文本：{text}\n\n"
            "{format_instructions}"
        )
        
        # 构建链
        chain = prompt | self.llm | self.json_parser
        
        # 执行
        return chain.invoke({"text": text})

# ============================================================
# 使用提取器
# ============================================================
extractor = ScheduleExtractor()

test_text = """
明天下午2点有一个非常重要的客户会议，
地点在北京市朝阳区建国路88号SOHO现代城。
会议主题是讨论Q1季度的产品规划，
预计持续2小时。
"""

try:
    event = extractor.extract(test_text)
    
    print("提取的日程信息：")
    print(f"  标题: {event.title}")
    print(f"  开始: {event.start_time.strftime('%Y年%m月%d日 %H:%M')}")
    if event.end_time:
        print(f"  结束: {event.end_time.strftime('%Y年%m月%d日 %H:%M')}")
    print(f"  地点: {event.location}")
    print(f"  描述: {event.description}")
except Exception as e:
    print(f"提取失败: {e}")
