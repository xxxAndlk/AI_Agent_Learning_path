class SubQueryDecomposer:
    """子查询分解器"""
    
    def __init__(self, llm_model: str = "gpt-5.4-mini"):
        """
        初始化分解器
        
        参数:
            llm_model: LLM模型名称
        """
        self.llm = ChatOpenAI(
            model_name=llm_model,
            temperature=0.3
        )
    
    def decompose(self, query: str) -> List[str]:
        """
        分解查询
        
        参数:
            query: 复杂查询
        
        返回:
            子查询列表
        """
        prompt = f"""请将以下复杂问题分解为多个简单的子问题。
        
要求：
1. 每个子问题应该是独立的、完整的
2. 子问题数量控制在3-5个
3. 使用问号结束每个子问题

原始问题: {query}

分解后的子问题（每行一个）:"""
        
        response = self.llm.predict(prompt)
        
        # 解析子问题
        sub_queries = [
            line.strip()
            for line in response.strip().split('\n')
            if line.strip() and '?' in line
        ]
        
        return sub_queries if sub_queries else [query]
