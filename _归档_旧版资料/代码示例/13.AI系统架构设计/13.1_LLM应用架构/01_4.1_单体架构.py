# 单体架构示例
class LLMApplication:
    """单体架构的LLM应用"""
    
    def __init__(self, config: dict):
        self.config = config
        self.llm_client = None
        self.vector_store = None
        self.cache = {}
        
    def initialize(self):
        """初始化所有组件"""
        # 初始化LLM客户端
        self.llm_client = OpenAIClient(
            api_key=self.config["api_key"],
            model=self.config.get("model", "gpt-5.4-mini")
        )
        
        # 初始化向量存储
        self.vector_store = FAISSStore(
            persist_directory=self.config.get("vector_db_path")
        )
        
        # 初始化提示词模板
        self.prompt_template = PromptTemplate(
            template=self.config.get("prompt_template", DEFAULT_TEMPLATE)
        )
        
    def process_request(self, user_input: str) -> str:
        """处理用户请求（单体架构，所有逻辑在一个方法中）"""
        # 1. 验证输入
        if not user_input or len(user_input.strip()) == 0:
            return "请输入有效的问题"
        
        # 2. 检查缓存
        cache_key = hash(user_input)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 3. RAG检索（如果启用）
        context = ""
        if self.vector_store:
            docs = self.vector_store.similarity_search(user_input, k=3)
            context = "\n\n".join([d.page_content for d in docs])
        
        # 4. 构建提示词
        prompt = self.prompt_template.format(
            context=context,
            question=user_input
        )
        
        # 5. 调用LLM
        response = self.llm_client.generate(prompt)
        
        # 6. 更新缓存
        if len(self.cache) < 1000:  # 简单缓存限制
            self.cache[cache_key] = response
        
        return response
    
    def shutdown(self):
        """关闭应用"""
        if self.vector_store:
            self.vector_store.close()
