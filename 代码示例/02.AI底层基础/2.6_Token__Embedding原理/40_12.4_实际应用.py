import numpy as np

class SemanticSearchEngine:
    """语义搜索引擎"""
    
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model = SentenceTransformer(model_name)
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, documents):
        """添加文档"""
        self.documents.extend(documents)
        
        # 重新计算嵌入
        self.embeddings = self.model.encode(
            self.documents,
            show_progress_bar=True
        )
    
    def search(self, query, top_k=5):
        """语义搜索"""
        # 编码查询
        query_embedding = self.model.encode([query])
        
        # 计算相似度
        similarities = cosine_similarity(query_embedding, self.embeddings)[0]
        
        # 排序
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                "document": self.documents[idx],
                "score": similarities[idx]
            })
        
        return results

# 使用示例
def demo_semantic_search():
    """演示语义搜索"""
    
    engine = SemanticSearchEngine()
    
    # 添加文档
    documents = [
        "深度学习是机器学习的一个分支",
        "自然语言处理用于文本分析",
        "计算机视觉用于图像识别",
        "机器学习包括监督学习和无监督学习",
        "Transformer模型在NLP领域取得了巨大成功",
    ]
    engine.add_documents(documents)
    
    # 搜索
    query = "什么是深度学习？"
    results = engine.search(query)
    
    print(f"查询: {query}")
    print("\n搜索结果:")
    for i, result in enumerate(results, 1):
        print(f"{i}. 相似度: {result['score']:.4f}")
        print(f"   文档: {result['document']}")
        print()

demo_semantic_search()
