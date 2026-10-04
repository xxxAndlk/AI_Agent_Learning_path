class QueryRewriter:
    """查询改写器"""
    
    def __init__(self, llm_model: str = "gpt-5.4-mini"):
        """
        初始化查询改写器
        
        参数:
            llm_model: LLM模型名称
        """
        self.llm = ChatOpenAI(
            model_name=llm_model,
            temperature=0.3
        )
    
    def rewrite(self, query: str) -> str:
        """
        改写查询
        
        参数:
            query: 原始查询
        
        返回:
            改写后的查询
        """
        prompt = f"""请将以下用户查询改写为更适合知识库检索的形式。
        
要求：
1. 保持原意，去除口语化表达
2. 使用正式的技术术语
3. 可以补充省略的主语和宾语
4. 长度适中，不要过长

原始查询: {query}

改写后的查询:"""
        
        response = self.llm.predict(prompt)
        return response.strip()
