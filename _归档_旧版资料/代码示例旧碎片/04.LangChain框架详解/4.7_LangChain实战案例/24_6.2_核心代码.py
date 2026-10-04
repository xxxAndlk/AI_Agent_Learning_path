"""
数据提取系统
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser


# 定义输出模式
class Person(BaseModel):
    """人物实体"""
    name: str = Field(description="姓名")
    age: Optional[int] = Field(description="年龄")
    role: Optional[str] = Field(description="角色/职位")
    email: Optional[str] = Field(description="邮箱")


class Organization(BaseModel):
    """组织实体"""
    name: str = Field(description="组织名称")
    type: Optional[str] = Field(description="类型")
    location: Optional[str] = Field(description="位置")


class ExtractedData(BaseModel):
    """提取的数据"""
    persons: List[Person] = Field(default_factory=list, description="人物列表")
    organizations: List[Organization] = Field(default_factory=list, description="组织列表")
    dates: List[str] = Field(default_factory=list, description="日期列表")
    locations: List[str] = Field(default_factory=list, description="地点列表")
    keywords: List[str] = Field(default_factory=list, description="关键词")


class DataExtractor:
    """数据提取器"""
    
    def __init__(
        self,
        model_name: str = "gpt-5.4-mini",
        api_key: Optional[str] = None,
    ):
        self.llm = ChatOpenAI(model=model_name, api_key=api_key)
        self.parser = PydanticOutputParser(pydantic_object=ExtractedData)
    
    def extract(
        self,
        text: str,
        schema: Optional[type[BaseModel]] = None,
    ) -> Dict[str, Any]:
        """
        从文本中提取数据
        
        Args:
            text: 源文本
            schema: 自定义数据模式
            
        Returns:
            提取的数据
        """
        if schema:
            return self._extract_custom(text, schema)
        else:
            return self._extract_default(text)
    
    def _extract_default(self, text: str) -> Dict[str, Any]:
        """默认提取"""
        prompt = ChatPromptTemplate.from_template(
            """从以下文本中提取结构化信息：

{text}

请提取：
1. 人物（姓名、年龄、角色）
2. 组织（名称、类型、地点）
3. 日期
4. 地点
5. 关键词

请以 JSON 格式返回结果。"""
        )
        
        chain = prompt | self.llm | self.parser
        result = chain.invoke({"text": text})
        
        return result.model_dump()
    
    def _extract_custom(
        self,
        text: str,
        schema: type[BaseModel],
    ) -> Dict[str, Any]:
        """自定义模式提取"""
        parser = PydanticOutputParser(pydantic_object=schema)
        
        prompt = ChatPromptTemplate.from_template(
            """从以下文本中提取信息：

{text}

{format_instructions}

只返回 JSON，不要有其他内容。"""
        )
        
        chain = prompt | self.llm | parser
        result = chain.invoke({
            "text": text,
            "format_instructions": parser.get_format_instructions(),
        })
        
        return result.model_dump()
    
    def extract_relations(
        self,
        text: str,
        entities: List[str],
    ) -> List[Dict[str, str]]:
        """提取实体关系"""
        entities_str = ", ".join(entities)
        
        prompt = f"""从以下文本中提取实体之间的关系：

文本：{text}

实体：{entities_str}

请识别实体之间的关系，例如：
- 张三 任职于 某公司
- 某公司 位于 某城市

请以 JSON 数组格式返回关系。"""
        
        response = self.llm.invoke(prompt).content
        
        try:
            import json
            return json.loads(response)
        except:
            return []


# 使用示例
if __name__ == "__main__":
    extractor = DataExtractor()
    
    # 测试文本
    text = """
    2024年1月15日，阿里巴巴集团创始人马云在杭州总部发表了重要讲话。
    他表示，阿里巴巴将继续投资于云计算和人工智能技术。
    阿里巴巴集团成立于1999年，总部位于中国杭州。
    同期，腾讯公司也在深圳举办了年度技术大会。
    """
    
    # 提取数据
    result = extractor.extract(text)
    
    print("提取的人物：")
    for person in result["persons"]:
        print(f"  - {person}")
    
    print("\n提取的组织：")
    for org in result["organizations"]:
        print(f"  - {org}")
    
    print(f"\n提取的日期: {result['dates']}")
    print(f"提取的地点: {result['locations']}")
    print(f"提取的关键词: {result['keywords']}")
