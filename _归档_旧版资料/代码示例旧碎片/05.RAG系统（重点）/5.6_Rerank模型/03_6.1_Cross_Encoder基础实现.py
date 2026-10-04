# 导入Cross Encoder和类型提示
from sentence_transformers import CrossEncoder
from typing import List, Tuple
import numpy as np

class CrossEncoderReranker:
    """Cross Encoder重排序器
    
    使用Cross-Encoder模型对文档进行精确重排序
    相比Bi-Encoder，Cross-Encoder能更好地理解查询和文档的语义关系
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        """
        初始化Cross Encoder
        
        参数:
            model_name: 模型名称，推荐使用BGE Reranker系列
                       - BAAI/bge-reranker-base (基础版，速度快)
                       - BAAI/bge-reranker-large (大模型版，效果更好)
        """
        # 创建CrossEncoder对象，加载预训练模型
        # 模型会自动下载（如果未缓存）并加载到内存
        self.model = CrossEncoder(model_name)
        # 打印加载信息
        print(f"[加载] Cross Encoder模型: {model_name}")
    
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5
    ) -> List[Tuple[str, float]]:
        """
        对文档进行重排序
        
        参数:
            query: 查询文本
            documents: 候选文档列表（通常是向量检索返回的结果）
            top_k: 返回前k个结果
        
        返回:
            [(文档, 分数), ...] 按分数降序排列
        """
        # 构建查询-文档对
        # Cross-Encoder需要将查询和文档配对输入
        # 格式为: [(query, doc1), (query, doc2), ...]
        query_doc_pairs = [(query, doc) for doc in documents]
        
        # 预测相关性分数
        # predict()方法会对每个查询-文档对进行编码并输出分数
        # 分数越高表示相关性越强
        scores = self.model.predict(query_doc_pairs)
        
        # 组合文档和分数
        # 使用zip将文档和对应分数配对
        doc_scores = list(zip(documents, scores))
        
        # 按分数降序排列
        # 使用sort方法，reverse=True实现降序
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top_k个结果
        return doc_scores[:top_k]
    
    def rerank_with_indices(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Tuple[int, str, float]]:
        """
        重排序并返回原始索引
        
        适用于需要知道原始文档位置的场景
        
        返回:
            [(原始索引, 文档, 分数), ...]
        """
        # 构建查询-文档对
        query_doc_pairs = [(query, doc) for doc in documents]
        
        # 预测分数
        scores = self.model.predict(query_doc_pairs)
        
        # 包含原始索引
        # enumerate()同时获取索引和内容
        # 格式: [(索引, 文档, 分数), ...]
        indexed_scores = [(i, doc, score) for i, (doc, score) in enumerate(zip(documents, scores))]
        
        # 按分数降序（第三列，即索引2）
        indexed_scores.sort(key=lambda x: x[2], reverse=True)
        
        # 返回top_k
        return indexed_scores[:top_k]


# ============ 使用示例 ============

def cross_encoder_example():
    """Cross Encoder使用示例"""
    
    # 初始化重排序器
    # 使用base版本，速度更快，适合实时应用
    # 如需更高精度可使用large版本
    reranker = CrossEncoderReranker("BAAI/bge-reranker-base")
    
    # 查询
    query = "什么是机器学习？"
    
    # 候选文档（假设这是向量检索返回的Top-10结果）
    candidate_docs = [
        "机器学习是人工智能的一个重要分支，它使计算机能够从数据中学习。",
        "深度学习是机器学习的一个子领域，使用神经网络进行学习。",
        "Python是一种流行的编程语言，广泛用于数据科学和机器学习。",
        "人工智能的目标是使机器表现出需要人类智能才能完成的行为。",
        "监督学习是机器学习的一种方法，使用标记数据进行训练。",
        "数据预处理是机器学习流程中的重要步骤。",
        "强化学习通过与环境交互来学习最优策略。",
        "特征工程对机器学习模型的性能有重要影响。",
        "集成学习结合多个模型来提高预测准确性。",
        "迁移学习可以将一个领域的知识应用到另一个领域。"
    ]
    
    # 打印查询和候选数量
    print(f"\n查询: {query}")
    print(f"候选文档数: {len(candidate_docs)}")
    print("\n" + "="*60)
    print("重排序结果（Top-5）")
    print("="*60)
    
    # 执行重排序
    # rerank()方法返回重排序后的文档列表
    results = reranker.rerank(query, candidate_docs, top_k=5)
    
    # 遍历结果并打印
    for rank, (doc, score) in enumerate(results, 1):
        # 打印排名、分数和文档内容（截取前80字符）
        print(f"\nRank {rank} (分数: {score:.4f}):")
        print(f"  {doc[:80]}...")


if __name__ == "__main__":
    cross_encoder_example()
