"""
混合检索与重排序示例
结合向量检索和关键词检索，提高召回率和准确率
"""

from typing import List, Dict, Tuple
import numpy as np
from rank_bm25 import BM25Okapi  # 需要安装: pip install rank-bm25


class HybridRetriever:
    """混合检索器：同时使用向量检索和BM25关键词检索，融合两种结果"""
    
    def __init__(self, documents: List[str], embeddings: np.ndarray):
        """
        初始化混合检索器
        
        参数:
            documents: 文档列表，每个元素是一个文档字符串
            embeddings: 文档的向量表示，形状为 (n_docs, embedding_dim)
        """
        self.documents = documents  # 保存文档列表，用于后续返回结果
        self.embeddings = embeddings  # 保存文档向量
        
        # 初始化BM25：将文档分词后构建BM25索引
        # BM25是一种经典的关键词检索算法，考虑词频和逆文档频率
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)
    
    def vector_search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        向量检索：使用余弦相似度找到最相似的文档
        
        参数:
            query_embedding: 查询的向量表示，形状为 (embedding_dim,)
            top_k: 返回前k个最相似的文档
        返回:
            results: [(文档索引, 相似度分数), ...] 按分数降序排列
        """
        # 计算余弦相似度：
        # 公式: cos(A,B) = (A·B) / (||A|| * ||B||)
        # 这里直接使用点积除以向量范数的乘积
        similarities = np.dot(self.embeddings, query_embedding) / (
            np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # 获取top-k索引：argsort返回升序排列的索引，[::-1]反转实现降序
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # 转换为结果列表：[(索引, 分数), ...]
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        关键词检索（BM25）：使用词匹配找到最相关的文档
        
        参数:
            query: 查询文本字符串
            top_k: 返回前k个最相关的文档
        返回:
            results: [(文档索引, BM25分数), ...] 按分数降序排列
        """
        # 将查询分词（转小写后按空格分割）
        tokenized_query = query.lower().split()
        
        # 计算BM25分数：每个文档与查询的相关性分数
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取top-k索引
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [(int(idx), float(scores[idx])) for idx in top_indices]
    
    def hybrid_search(
        self,
        query: str,
        query_embedding: np.ndarray,
        top_k: int = 10,
        alpha: float = 0.7
    ) -> List[Dict]:
        """
        混合检索：融合向量检索和关键词检索的结果
        
        参数:
            query: 查询文本，用于关键词检索
            query_embedding: 查询向量，用于向量检索
            top_k: 返回前k个结果
            alpha: 向量检索权重 (0-1)，alpha=1表示只用向量检索，alpha=0表示只用关键词检索
        返回:
            results: 包含文档信息和各方法分数的字典列表
        """
        # 第1步：执行向量检索，返回2*top_k个候选（扩大候选集以提高召回）
        vector_results = dict(self.vector_search(query_embedding, top_k=top_k*2))
        
        # 第2步：执行关键词检索，返回2*top_k个候选
        keyword_results = dict(self.keyword_search(query, top_k=top_k*2))
        
        # 第3步：归一化分数 - 两种检索方法的分数体系不同，需要归一化到同一尺度
        # 向量检索分数归一化
        if vector_results:
            max_vec = max(vector_results.values())  # 找出最大分数
            # 每个分数除以最大分数，实现0-1归一化
            vector_results = {k: v/max_vec for k, v in vector_results.items()}
        
        # 关键词检索分数归一化
        if keyword_results:
            max_kw = max(keyword_results.values())
            keyword_results = {k: v/max_kw for k, v in keyword_results.items()}
        
        # 第4步：融合分数 - 合并两种检索方法的结果
        # 获取所有文档索引的并集
        all_indices = set(vector_results.keys()) | set(keyword_results.keys())
        fused_scores = {}
        
        # 对每个文档计算融合分数
        for idx in all_indices:
            vec_score = vector_results.get(idx, 0)  # 向量检索分数，未命中为0
            kw_score = keyword_results.get(idx, 0)  # 关键词检索分数，未命中为0
            # 加权融合：alpha权重给向量检索，(1-alpha)权重给关键词检索
            fused_scores[idx] = alpha * vec_score + (1 - alpha) * kw_score
        
        # 第5步：排序并返回结果
        # 按融合分数降序排列
        sorted_results = sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 构建结果列表
        results = []
        for idx, score in sorted_results[:top_k]:
            results.append({
                "index": idx,  # 文档索引
                "document": self.documents[idx],  # 文档内容
                "score": score,  # 融合后的总分数
                "vector_score": vector_results.get(idx, 0),  # 向量检索分数（归一化后）
                "keyword_score": keyword_results.get(idx, 0)  # 关键词检索分数（归一化后）
            })
        
        return results


class Reranker:
    """重排序器：对初步检索结果进行二次排序，提高准确率"""
    
    def __init__(self):
        """初始化重排序器"""
        pass  # 简化实现，无需初始化额外参数
    
    def rerank(self, query: str, documents: List[Dict], top_k: int = 5) -> List[Dict]:
        """
        重排序：使用多维特征对文档重新排序
        
        参数:
            query: 查询字符串
            documents: 初步检索结果列表，每个元素是包含"document"和"score"键的字典
            top_k: 返回前k个结果
        返回:
            重排序后的结果列表
        """
        # 第1步：提取查询关键词
        query_words = set(query.lower().split())
        
        # 用于存储每个文档的重排序分数
        scored_docs = []
        
        # 第2步：遍历每个文档，计算多维特征
        for doc in documents:
            doc_text = doc["document"].lower()
            doc_words = set(doc_text.split())
            
            # 特征1：Jaccard相似度 - 衡量查询词与文档词的交集程度
            # Jaccard = |A ∩ B| / |A ∪ B|
            intersection = len(query_words & doc_words)
            union = len(query_words | doc_words)
            jaccard = intersection / union if union > 0 else 0
            
            # 特征2：位置权重 - 查询词在文档中出现越早越好
            position_score = 0
            for word in query_words:
                if word in doc_text:
                    # 找到词首次出现的位置，位置越靠前分数越高
                    position = doc_text.index(word)
                    # 使用1/(1+position)公式，位置0得分为1，位置1得分为0.5，以此类推
                    position_score += 1 / (1 + position)
            
            # 第3步：计算综合重排序分数
            # 权重分配：原始分数50%，Jaccard相似度30%，位置权重20%
            final_score = doc["score"] * 0.5 + jaccard * 0.3 + position_score * 0.2
            
            # 将重排序分数添加到文档信息中
            scored_docs.append({**doc, "rerank_score": final_score})
        
        # 第4步：按重排序分数降序排序
        scored_docs.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # 返回top-k结果
        return scored_docs[:top_k]


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 准备示例文档数据
    documents = [
        "Python是一种高级编程语言，广泛用于AI开发",
        "Go语言以并发性能著称，适合云原生应用",
        "Python的库生态系统丰富，包括PyTorch、TensorFlow",
        "Go的编译速度快，部署简单",
        "机器学习是人工智能的核心技术",
        "深度学习使用神经网络进行学习"
    ]
    
    # 生成模拟向量（实际应用中应该使用真实的embedding模型生成）
    # 这里生成形状为 (6, 384) 的随机向量，384是常见embedding维度
    embeddings = np.random.rand(len(documents), 384)
    
    # 创建混合检索器实例
    retriever = HybridRetriever(documents, embeddings)
    
    # 执行混合检索
    query = "Python AI开发"
    query_embedding = np.random.rand(384)  # 模拟查询向量
    
    # 调用混合检索方法，获取前5个结果
    results = retriever.hybrid_search(query, query_embedding, top_k=5)
    
    # 打印混合检索结果
    print("混合检索结果:")
    for i, result in enumerate(results, 1):
        # 只显示前30个字符，避免输出过长
        print(f"{i}. {result['document'][:30]}... (分数: {result['score']:.3f})")
    
    # 执行重排序
    reranker = Reranker()
    reranked = reranker.rerank(query, results, top_k=3)
    
    # 打印重排序后的结果
    print("\n重排序后:")
    for i, result in enumerate(reranked, 1):
        print(f"{i}. {result['document'][:30]}... (分数: {result['rerank_score']:.3f})")
