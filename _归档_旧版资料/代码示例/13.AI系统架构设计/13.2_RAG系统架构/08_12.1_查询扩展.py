class QueryExpander:
    """查询扩展器"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        初始化查询扩展器
        
        参数:
            model_name: 嵌入模型名称
        """
        from sentence_transformers import SentenceTransformer
        
        self.model = SentenceTransformer(model_name)
        
        # 同义词词典
        self.synonym_dict = {
            "电脑": ["计算机", "笔记本", "台式机"],
            "手机": ["智能手机", "移动电话"],
            "AI": ["人工智能", "机器学习", "深度学习"]
        }
    
    def expand(self, query: str, num_terms: int = 3) -> str:
        """
        扩展查询
        
        参数:
            query: 原始查询
            num_terms: 扩展词数量
        
        返回:
            扩展后的查询
        """
        expanded_terms = []
        
        # 基于同义词扩展
        for word, synonyms in self.synonym_dict.items():
            if word in query:
                expanded_terms.extend(synonyms[:num_terms])
        
        # 限制扩展词数量
        expanded_terms = expanded_terms[:num_terms]
        
        # 构建扩展查询
        if expanded_terms:
            expanded_query = f"{query} {' '.join(expanded_terms)}"
            return expanded_query
        
        return query
