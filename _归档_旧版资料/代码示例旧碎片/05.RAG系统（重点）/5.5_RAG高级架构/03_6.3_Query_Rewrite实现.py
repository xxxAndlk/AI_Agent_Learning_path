"""
Query Rewrite实现
展示多种查询重写策略
"""

from typing import List, Dict  # 导入类型提示
import re  # 导入正则表达式模块

class QueryRewriter:
    """查询重写器"""
    
    def __init__(self):
        # 初始化同义词词典
        self.synonym_dict = {
            "Python": ["Python编程", "Python语言"],  # Python的同义词
            "AI": ["人工智能", "Artificial Intelligence"],  # AI的同义词
            "ML": ["机器学习", "Machine Learning"],  # ML的同义词
            "深度学习": ["神经网络", "Deep Learning"],  # 深度学习的同义词
        }
    
    def expand_query(self, query: str) -> List[str]:
        """查询扩展：添加同义词"""
        expanded = [query]  # 原始查询作为第一个元素
        # 遍历同义词词典
        for key, synonyms in self.synonym_dict.items():
            # 检查查询中是否包含词典中的关键词
            if key.lower() in query.lower():
                # 用每个同义词替换关键词，生成新的查询变体
                for syn in synonyms:
                    expanded.append(query.replace(key, syn))
        # 最多返回5个查询变体
        return expanded[:5]
    
    def decompose_query(self, query: str) -> List[str]:
        """查询分解：将复杂查询拆分为子查询"""
        # 检测并列关系（和、与、vs）
        if "和" in query or "与" in query or "vs" in query.lower():
            # 使用正则表达式按连接词分割查询
            parts = re.split(r'和|与|vs', query, flags=re.IGNORECASE)
            # 返回分割后的子查询（去除空字符串）
            return [p.strip() for p in parts if p.strip()]
        # 无需分解，返回原始查询
        return [query]
    
    def hyde_rewrite(self, query: str) -> str:
        """HyDE（假设文档嵌入）：生成假设答案"""
        # 简化为添加引导词，形成假设性的查询
        return f"关于'{query}'的详细信息"


# 使用示例
if __name__ == "__main__":
    rewriter = QueryRewriter()
    
    query = "Python和Java的机器学习应用"
    print(f"原始查询: {query}")
    print(f"扩展后: {rewriter.expand_query(query)}")
    print(f"分解后: {rewriter.decompose_query(query)}")
