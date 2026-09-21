"""
Rerank模型实现
使用Cross-Encoder进行精确重排序
"""

from typing import List, Dict  # 导入类型提示
import numpy as np  # 导入numpy用于数值计算

class Reranker:
    """重排序器
    
    使用Cross-Encoder模型对初步检索结果进行精确重排序
    """
    
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """
        初始化重排序器
        
        参数:
            model_name: 交叉编码器模型名称
        """
        try:
            # 尝试导入Cross-Encoder模型
            from sentence_transformers import CrossEncoder
            self.model = CrossEncoder(model_name)  # 加载预训练的Cross-Encoder模型
            self.available = True  # 标记模型可用
        except ImportError:
            # 如果导入失败，打印警告并使用备用方法
            print("警告: sentence-transformers未安装，使用简单重排序")
            self.available = False
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        initial_scores: List[float] = None,
        top_k: int = 5
    ) -> List[Dict]:
        """
        重排序文档
        
        参数:
            query: 查询文本
            documents: 候选文档列表
            initial_scores: 初始检索分数（可选）
            top_k: 返回数量
        返回:
            重排序后的结果
        """
        # 空文档列表直接返回空结果
        if not documents:
            return []
        
        if self.available:
            # 使用Cross-Encoder进行精确评分
            # Cross-Encoder将查询和文档一起编码，捕获更精细的交互信息
            # 创建查询-文档对列表
            pairs = [(query, doc) for doc in documents]
            # 批量预测相关性分数
            scores = self.model.predict(pairs)
        else:
            # 备用：使用简单的关键词匹配进行重排序
            scores = self._simple_rerank(query, documents)
        
        # 如果提供了初始分数，将其与重排序分数融合
        if initial_scores and len(initial_scores) == len(documents):
            # 加权融合：重排序分数权重0.7，初始分数权重0.3
            final_scores = 0.7 * scores + 0.3 * np.array(initial_scores)
        else:
            final_scores = scores
        
        # 构建结果列表
        results = []
        for i, (doc, score) in enumerate(zip(documents, final_scores)):
            results.append({
                "index": i,  # 原始索引
                "content": doc,  # 文档内容
                "rerank_score": float(score),  # 重排序分数
                "initial_score": initial_scores[i] if initial_scores else None  # 初始分数
            })
        
        # 按重排序分数降序排序
        results.sort(key=lambda x: x["rerank_score"], reverse=True)
        
        # 返回top_k个结果
        return results[:top_k]
    
    def _simple_rerank(self, query: str, documents: List[str]) -> np.ndarray:
        """简单重排序（基于关键词匹配）"""
        # 将查询分词为词集合
        query_words = set(query.lower().split())
        scores = []
        
        for doc in documents:
            # 将文档分词为词集合
            doc_words = set(doc.lower().split())
            # 计算Jaccard相似度：交集/并集
            intersection = len(query_words & doc_words)  # 共同出现的词数
            union = len(query_words | doc_words)  # 所有不同的词数
            score = intersection / union if union > 0 else 0
            
            # 额外加分：查询词在文档开头（前100字符）出现
            for word in query_words:
                if word in doc.lower()[:100]:
                    score += 0.1
            
            # 限制分数最高为1.0
            scores.append(min(score, 1.0))
        
        return np.array(scores)


class TwoStageRetriever:
    """两阶段检索器
    
    第一阶段：快速检索（向量/BM25）获取候选集
    第二阶段：精确重排序
    """
    
    def __init__(
        self,
        hybrid_engine: 'HybridSearchEngine',
        reranker: Reranker,
        stage1_top_k: int = 50,
        stage2_top_k: int = 5
    ):
        """
        初始化两阶段检索器
        
        参数:
            hybrid_engine: 混合搜索引擎
            reranker: 重排序器
            stage1_top_k: 第一阶段返回数量
            stage2_top_k: 第二阶段返回数量
        """
        self.hybrid_engine = hybrid_engine  # 存储混合搜索引擎
        self.reranker = reranker  # 存储重排序器
        self.stage1_top_k = stage1_top_k  # 存储第一阶段top_k
        self.stage2_top_k = stage2_top_k  # 存储第二阶段top_k
    
    def retrieve(self, query: str) -> List[Dict]:
        """
        执行两阶段检索
        
        参数:
            query: 查询文本
        返回:
            最终检索结果
        """
        print(f"\n查询: {query}")
        print("=" * 50)
        
        # 第一阶段：使用混合检索快速获取候选集
        print(f"[阶段1] 混合检索 Top-{self.stage1_top_k}...")
        stage1_results = self.hybrid_engine.hybrid_search(
            query, 
            top_k=self.stage1_top_k
        )
        
        # 空结果直接返回
        if not stage1_results:
            return []
        
        # 提取文档内容和初始分数
        documents = [r["content"] for r in stage1_results]
        initial_scores = [r["score"] for r in stage1_results]
        
        print(f"  检索到 {len(documents)} 个候选文档")
        
        # 第二阶段：使用重排序器进行精确排序
        print(f"[阶段2] 重排序 Top-{self.stage2_top_k}...")
        stage2_results = self.reranker.rerank(
            query,
            documents,
            initial_scores,
            top_k=self.stage2_top_k
        )
        
        print(f"  重排序完成")
        
        return stage2_results


# 使用示例
if __name__ == "__main__":
    from ai应用开发学习文档 import HybridSearchEngine
    
    # 准备测试文档
    documents = [
        "Python是最受欢迎的编程语言之一，特别适合数据科学",
        "Java是一种静态类型的编程语言，广泛用于企业级开发",
        "JavaScript是Web开发的核心语言，运行在浏览器中",
        "Python在机器学习和人工智能领域有广泛应用",
        "深度学习框架PyTorch和TensorFlow都支持Python",
        "Python的语法简洁，学习曲线平缓，适合初学者",
        "Java和Python都是面向对象的编程语言",
        "Python的性能不如C++，但开发效率更高"
    ]
    
    # 创建搜索引擎
    hybrid_engine = HybridSearchEngine(documents)
    reranker = Reranker()
    
    # 创建两阶段检索器
    retriever = TwoStageRetriever(
        hybrid_engine,
        reranker,
        stage1_top_k=20,
        stage2_top_k=3
    )
    
    # 测试检索
    queries = [
        "Python机器学习",
        "编程语言对比"
    ]
    
    for query in queries:
        results = retriever.retrieve(query)
        print("\n最终结果:")
        for i, r in enumerate(results, 1):
            print(f"  {i}. [{r['rerank_score']:.3f}] {r['content']}")
