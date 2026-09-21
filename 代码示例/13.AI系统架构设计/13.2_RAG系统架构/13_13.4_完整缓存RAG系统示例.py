import numpy as np
class CachedRAGSystem:
    """带缓存的RAG系统"""
    
    def __init__(
        self,
        docs_dir: str = "./docs",
        embedding_model: str = "text-embedding-3-small",
        llm_model: str = "gpt-5.4-mini",
        use_cache: bool = True
    ):
        """
        初始化RAG系统
        
        参数:
            docs_dir: 文档目录
            embedding_model: 嵌入模型
            llm_model: LLM模型
            use_cache: 是否使用缓存
        """
        self.docs_dir = docs_dir
        self.embedding_model = embedding_model
        self.llm_model = llm_model
        self.use_cache = use_cache
        
        # 初始化组件
        self.embeddings = OpenAIEmbeddings(model=embedding_model)
        self.llm = ChatOpenAI(model_name=llm_model, temperature=0)
        
        # 初始化缓存
        self.query_cache = QueryCache(max_size=1000)
        self.embedding_cache = EmbeddingCache(max_size=5000)
        
        self.vector_store = None
        self.qa_chain = None
    
    def _get_embedding(self, text: str) -> np.ndarray:
        """获取嵌入向量（带缓存）"""
        # 尝试从缓存获取
        cached = self.embedding_cache.get(text)
        if cached is not None:
            return cached
        
        # 计算嵌入
        embedding = self.embeddings.embed_query(text)
        embedding = np.array(embedding)
        
        # 缓存结果
        if self.use_cache:
            self.embedding_cache.set(text, embedding)
        
        return embedding
    
    def query(self, question: str) -> Dict[str, Any]:
        """
        执行问答（带缓存）
        
        参数:
            question: 用户问题
        
        返回:
            答案和源文档
        """
        # 尝试从缓存获取
        if self.use_cache:
            cached_result = self.query_cache.get(question)
            if cached_result:
                print("_cache: 命中缓存")
                return cached_result
        
        # 正常检索和生成
        if not self.qa_chain:
            self.setup_qa_chain()
        
        result = self.qa_chain.invoke({"query": question})
        
        response = {
            "answer": result["result"],
            "source_documents": [
                doc.page_content for doc in result["source_documents"]
            ]
        }
        
        # 缓存结果
        if self.use_cache:
            self.query_cache.set(question, response)
        
        return response
    
    def build_vector_store(self, chunks: List):
        """构建向量存储"""
        self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        print(f"✅ 向量存储已构建，包含 {len(chunks)} 个文档块")
    
    def setup_qa_chain(self, top_k: int = 3):
        """设置问答链"""
        if not self.vector_store:
            raise ValueError("向量存储未初始化")
        
        retriever = self.vector_store.as_retriever(
            search_kwargs={"k": top_k}
        )
        
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=True
        )
