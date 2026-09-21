"""
关键词提取器实现
使用CommaSeparatedListOutputParser实现高效的关键词提取
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from typing import List

# ============================================================
# 定义关键词提取器
# ============================================================
class KeywordExtractor:
    """
    关键词提取器类
    封装完整的提取逻辑
    """
    
    def __init__(self, max_keywords: int = 10):
        self.max_keywords = max_keywords
        self.parser = CommaSeparatedListOutputParser()
        self.prompt = ChatPromptTemplate.from_template(
            "从以下文章中提取{max_keywords}个最重要的关键词。"
            "只返回关键词列表，用逗号分隔，不要有其他内容。\n\n"
            "文章：{content}"
        )
        self.llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
        self.chain = self.prompt | self.llm | self.parser
    
    def extract(self, content: str) -> List[str]:
        """提取关键词"""
        # 调用链获取原始结果
        raw_result = self.chain.invoke({
            "content": content,
            "max_keywords": self.max_keywords
        })
        
        # 确保不超过最大数量
        return raw_result[:self.max_keywords]

# ============================================================
# 使用关键词提取器
# ============================================================
extractor = KeywordExtractor(max_keywords=8)

article = """
人工智能（Artificial Intelligence，AI）是计算机科学的一个分支，
它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式
做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、
自然语言处理和专家系统等。

机器学习是人工智能的核心，是使计算机具有智能的根本途径。
它是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、
算法复杂度理论等多门学科。机器学习专门研究计算机怎样模拟或实现
人类的学习行为，以获取新的知识或技能，重新组织已有的知识结构
使之不断改善自身的性能。

深度学习是机器学习的分支，是一种以人工神经网络为架构，
对数据进行表征学习的算法。深度学习在计算机视觉、语音识别、
自然语言处理等领域取得了突破性进展。
"""

keywords = extractor.extract(article)

print("提取的关键词：")
for i, keyword in enumerate(keywords, 1):
    print(f"  {i}. {keyword}")
