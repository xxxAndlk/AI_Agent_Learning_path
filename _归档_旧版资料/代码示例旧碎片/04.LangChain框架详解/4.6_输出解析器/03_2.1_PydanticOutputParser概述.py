"""
PydanticOutputParser基础用法
演示如何使用Pydantic模型定义输出结构并解析LLM响应
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional

# ============================================================
# 步骤1：定义Pydantic数据模型
# ============================================================
class MovieReview(BaseModel):
    """
    电影评论数据模型
    展示Pydantic的字段定义和验证功能
    """
    
    # 电影名称，必填字段
    title: str = Field(description="电影名称")
    
    # 评分，范围0-10
    rating: float = Field(description="评分，范围0-10")
    
    # 评论摘要，必填，不超过100字
    summary: str = Field(description="简短评论摘要，不超过100字")
    
    # 优点列表
    pros: List[str] = Field(description="电影优点列表")
    
    # 缺点列表
    cons: List[str] = Field(description="电影缺点列表")
    
    # 是否推荐，可选字段默认为True
    recommended: Optional[bool] = Field(default=True, description="是否推荐观看")
    
    # 自定义验证器：确保评分在有效范围内
    @field_validator('rating')
    def validate_rating(cls, v):
        if not 0 <= v <= 10:
            raise ValueError('评分必须在0-10之间')
        return round(v, 1)  # 四舍五入到一位小数
    
    @field_validator('summary')
    def validate_summary(cls, v):
        if len(v) > 100:
            raise ValueError('摘要不能超过100字')
        return v

# ============================================================
# 步骤2：创建PydanticOutputParser
# ============================================================
# 将Pydantic模型包装为输出解析器
parser = PydanticOutputParser(pydantic_object=MovieReview)

# 获取自动生成的格式说明
format_instructions = parser.get_format_instructions()
print("格式说明：")
print(format_instructions)
print("=" * 50)

# ============================================================
# 步骤3：构建Prompt模板
# ============================================================
# 模板中包含解析器生成的格式说明
prompt = ChatPromptTemplate.from_template(
    "请根据以下电影信息生成结构化评论。\n\n"
    "电影信息：{movie_info}\n\n"
    "{format_instructions}"
)

# ============================================================
# 步骤4：创建LLM和LCEL链
# ============================================================
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)
chain = prompt | llm | parser

# ============================================================
# 步骤5：执行并处理结果
# ============================================================
movie_info = """
电影《盗梦空间》是一部2010年的科幻悬疑片，由克里斯托弗·诺兰执导，
莱昂纳多·迪卡普里奥主演。影片讲述了造梦师柯布通过进入他人梦境
来窃取机密并改变他人想法的故事。
"""

# 执行链式调用
review = chain.invoke({"movie_info": movie_info})

# 输出是完整的Pydantic对象
print(f"电影: {review.title}")
print(f"评分: {review.rating}")
print(f"摘要: {review.summary}")
print(f"优点: {review.pros}")
print(f"缺点: {review.cons}")
print(f"推荐: {review.recommended}")
