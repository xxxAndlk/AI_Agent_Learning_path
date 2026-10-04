"""
综合示例：结构化问答系统
展示多种解析器在实际项目中的应用
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import (
    JsonOutputParser,
    PydanticOutputParser,
    CommaSeparatedListOutputParser,
    OutputFixingParser
)
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

# ============================================================
# 定义数据模型
# ============================================================

class AnswerFormat(Enum):
    """答案格式枚举"""
    BRIEF = "简要"
    DETAILED = "详细"
    STEP_BY_STEP = "分步"

class SourceType(Enum):
    """来源类型"""
    DOCUMENT = "文档"
    WEB = "网页"
    KNOWLEDGE = "知识库"
    UNKNOWN = "未知"

class QAResult(BaseModel):
    """问答结果模型"""
    question: str = Field(description="原始问题")
    answer: str = Field(description="答案内容")
    format_type: AnswerFormat = Field(description="答案格式")
    confidence: float = Field(description="置信度，0-1之间")
    sources: List[str] = Field(description="参考来源")
    source_type: SourceType = Field(description="来源类型")
    related_keywords: List[str] = Field(description="相关关键词")
    follow_up_questions: Optional[List[str]] = Field(
        default=None,
        description="可能的跟进问题"
    )

# ============================================================
# 创建解析器
# ============================================================

# 主解析器
qa_parser = PydanticOutputParser(pydantic_object=QAResult)

# 关键词提取解析器
keyword_parser = CommaSeparatedListOutputParser()

# 修复解析器
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
fixing_parser = OutputFixingParser(
    parser=qa_parser,
    llm=llm,
    max_retries=2
)

# ============================================================
# 构建问答系统
# ============================================================

class QASystem:
    """结构化问答系统"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)
        self.qa_parser = fixing_parser
        self.keyword_parser = keyword_parser
        self._setup_prompts()
    
    def _setup_prompts(self):
        """设置提示词模板"""
        self.qa_prompt = ChatPromptTemplate.from_template(
            "你是一个专业的问答系统。请根据给定的上下文回答用户问题。\n\n"
            "上下文：{context}\n\n"
            "问题：{question}\n\n"
            "{format_instructions}"
        )
        
        self.keyword_prompt = ChatPromptTemplate.from_template(
            "从以下问题中提取3-5个关键词。\n\n"
            "问题：{question}\n\n"
            "{format_instructions}"
        )
    
    def ask(self, question: str, context: str = "") -> QAResult:
        """提问并获取结构化答案"""
        
        # 构建问答链
        qa_chain = self.qa_prompt | self.llm | self.qa_parser
        
        # 执行问答
        result = qa_chain.invoke({
            "question": question,
            "context": context or "无额外上下文"
        })
        
        # 提取关键词
        keyword_chain = self.keyword_prompt | self.llm | self.keyword_parser
        keywords = keyword_chain.invoke({"question": question})
        result.related_keywords = keywords
        
        return result

# ============================================================
# 使用问答系统
# ============================================================
qa_system = QASystem()

# 示例问题
question = "什么是Python的列表推导式？请给出一个例子。"

print("问题:", question)
print("=" * 50)

result = qa_system.ask(question)

print(f"答案: {result.answer}")
print(f"格式: {result.format_type.value}")
print(f"置信度: {result.confidence:.2%}")
print(f"关键词: {result.related_keywords}")

if result.follow_up_questions:
    print(f"跟进问题: {result.follow_up_questions}")
