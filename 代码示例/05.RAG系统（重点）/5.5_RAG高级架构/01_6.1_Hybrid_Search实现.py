"""
Hybrid Search实现
结合向量检索和BM25关键词检索
"""

from typing import List, Dict, Tuple  # 导入类型提示相关类型：列表、字典、元组
import numpy as np  # 导入numpy库，用于数值计算
from rank_bm25 import BM25Okapi  # 导入BM25算法实现
from sentence_transformers import SentenceTransformer  # 导入Sentence-Transformers库

class HybridSearchEngine:
    """混合搜索引擎
    
    结合以下检索方式：
    1. 向量检索（语义相似度）
    2. BM25检索（关键词匹配）
    3. 结果融合与重排序
    """
    
    def __init__(
        self,
        documents: List[str],
        vector_weight: float = 0.7,
        keyword_weight: float = 0.3
    ):
        """
        初始化混合搜索引擎
        
        参数:
            documents: 文档列表
            vector_weight: 向量检索权重（0-1）
            keyword_weight: 关键词检索权重（0-1）
        """
        self.documents = documents  # 保存文档列表
        self.vector_weight = vector_weight  # 保存向量检索权重
        self.keyword_weight = keyword_weight  # 保存关键词检索权重
        
        # 初始化向量模型，加载预训练的Sentence-Transformers模型
        print("加载向量模型...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')  # 使用轻量级模型all-MiniLM-L6-v2
        self.document_embeddings = self.encoder.encode(documents)  # 将所有文档编码为向量
        
        # 初始化BM25，构建BM25索引
        print("构建BM25索引...")
        # 对每个文档进行分词（转小写后按空格分割）
        tokenized_docs = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized_docs)  # 创建BM25对象
        
        print(f"索引构建完成: {len(documents)} 个文档")  # 打印完成信息
    
    def vector_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        向量检索
        
        参数:
            query: 查询文本
            top_k: 返回数量
        返回:
            [(文档索引, 相似度), ...]
        """
        # 将查询编码为向量
        query_embedding = self.encoder.encode([query])[0]
        
        # 计算余弦相似度：使用点积除以两个向量的模的乘积
        # np.dot计算点积，np.linalg.norm计算向量的L2范数（模）
        similarities = np.dot(self.document_embeddings, query_embedding) / (
            np.linalg.norm(self.document_embeddings, axis=1) *  # 计算所有文档向量的模
            np.linalg.norm(query_embedding)  # 计算查询向量的模
        )
        
        # 获取相似度最高的top_k个文档索引
        # np.argsort返回升序排列的索引，[::-1]反转实现降序，[:top_k]取前k个
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # 将结果转换为列表格式：[(索引, 相似度), ...]
        return [(int(idx), float(similarities[idx])) for idx in top_indices]
    
    def keyword_search(self, query: str, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        关键词检索（BM25）
        
        参数:
            query: 查询文本
            top_k: 返回数量
        返回:
            [(文档索引, 分数), ...]
        """
        # 对查询进行分词
        tokenized_query = query.lower().split()
        
        # 使用BM25计算每个文档与查询的相关性分数
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取分数最高的top_k个文档索引
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        # 归一化分数到0-1范围：除以最大分数
        max_score = max(scores) if max(scores) > 0 else 1  # 防止除零
        
        return [(int(idx), float(scores[idx] / max_score)) for idx in top_indices]
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 10,
        fusion_method: str = "rrf"  # rrf/linear/distribution
    ) -> List[Dict]:
        """
        混合检索
        
        参数:
            query: 查询文本
            top_k: 返回数量
            fusion_method: 融合方法（rrf/linear/distribution）
        返回:
            检索结果列表
        """
        # 分别进行向量检索和关键词检索，检索更多候选以保证融合后有足够结果
        vector_results = self.vector_search(query, top_k=top_k * 2)
        keyword_results = self.keyword_search(query, top_k=top_k * 2)
        
        # 根据指定的融合方法融合结果
        if fusion_method == "rrf":
            # 倒数排序融合
            fused_scores = self._reciprocal_rank_fusion(vector_results, keyword_results)
        elif fusion_method == "linear":
            # 线性加权融合
            fused_scores = self._linear_fusion(vector_results, keyword_results)
        else:
            # 概率分布融合
            fused_scores = self._distribution_fusion(vector_results, keyword_results)
        
        # 构建最终结果列表
        results = []
        # 按融合分数降序排序并取top_k个
        for doc_idx, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)[:top_k]:
            results.append({
                "index": doc_idx,  # 文档索引
                "content": self.documents[doc_idx],  # 文档内容
                "score": score,  # 融合后的总分
                "vector_score": next((s for i, s in vector_results if i == doc_idx), 0),  # 向量检索分数
                "keyword_score": next((s for i, s in keyword_results if i == doc_idx), 0)  # 关键词检索分数
            })
        
        return results
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Tuple[int, float]],
        keyword_results: List[Tuple[int, float]],
        k: int = 60
    ) -> Dict[int, float]:
        """
        倒数排序融合（RRF）
        
        RRF公式: score = Σ 1 / (k + rank)
        k=60是经验值，用于平滑低排名项的影响
        
        参数:
            vector_results: 向量检索结果
            keyword_results: 关键词检索结果
            k: 常数参数
        返回:
            融合后的分数字典
        """
        scores = {}  # 初始化分数字典
        
        # 处理向量检索结果：根据排名计算RRF分数
        for rank, (doc_idx, _) in enumerate(vector_results):
            # 累加RRF分数：1/(k+rank)，排名越高分数越高
            scores[doc_idx] = scores.get(doc_idx, 0) + 1.0 / (k + rank)
        
        # 处理关键词检索结果：同样方式累加
        for rank, (doc_idx, _) in enumerate(keyword_results):
            scores[doc_idx] = scores.get(doc_idx, 0) + 1.0 / (k + rank)
        
        return scores
    
    def _linear_fusion(
        self,
        vector_results: List[Tuple[int, float]],
        keyword_results: List[Tuple[int, float]]
    ) -> Dict[int, float]:
        """线性加权融合"""
        scores = {}
        
        # 将向量检索分数按权重累加
        for doc_idx, score in vector_results:
            scores[doc_idx] = scores.get(doc_idx, 0) + score * self.vector_weight
        
        # 将关键词检索分数按权重累加
        for doc_idx, score in keyword_results:
            scores[doc_idx] = scores.get(doc_idx, 0) + score * self.keyword_weight
        
        return scores
    
    def _distribution_fusion(
        self,
        vector_results: List[Tuple[int, float]],
        keyword_results: List[Tuple[int, float]]
    ) -> Dict[int, float]:
        """基于分布的融合（概率乘积）"""
        scores = {}
        
        # 计算各检索结果的分数总和，用于归一化为概率
        vector_total = sum(s for _, s in vector_results)
        keyword_total = sum(s for _, s in keyword_results)
        
        # 将向量分数归一化为概率后按权重相乘
        for doc_idx, score in vector_results:
            prob = score / vector_total if vector_total > 0 else 0
            scores[doc_idx] = scores.get(doc_idx, 1.0) * (prob ** self.vector_weight)
        
        # 将关键词分数归一化为概率后按权重相乘
        for doc_idx, score in keyword_results:
            prob = score / keyword_total if keyword_total > 0 else 0
            scores[doc_idx] = scores.get(doc_idx, 1.0) * (prob ** self.keyword_weight)
        
        return scores


# 使用示例
if __name__ == "__main__":
    # 准备测试文档
    documents = [
        "Python是一种高级编程语言，广泛用于数据科学和机器学习",
        "机器学习是人工智能的一个分支，使用算法从数据中学习",
        "深度学习是机器学习的一种，使用多层神经网络",
        "PyTorch是一个开源的深度学习框架，支持动态计算图",
        "TensorFlow是Google开发的机器学习框架",
        "自然语言处理是AI的重要应用领域，处理人类语言",
        "计算机视觉让计算机能够理解和分析图像",
        "强化学习通过与环境交互来学习最优策略"
    ]
    
    # 创建混合搜索引擎，指定向量权重0.6，关键词权重0.4
    engine = HybridSearchEngine(documents, vector_weight=0.6, keyword_weight=0.4)
    
    # 测试查询
    queries = [
        "Python机器学习框架",
        "深度学习算法",
        "AI应用"
    ]
    
    for query in queries:
        print(f"\n查询: {query}")
        print("-" * 50)
        
        # 使用不同融合方法测试
        for method in ["rrf", "linear", "distribution"]:
            results = engine.hybrid_search(query, top_k=3, fusion_method=method)
            print(f"\n  方法: {method}")
            for i, r in enumerate(results, 1):
                print(f"    {i}. [{r['score']:.3f}] {r['content'][:40]}...")
