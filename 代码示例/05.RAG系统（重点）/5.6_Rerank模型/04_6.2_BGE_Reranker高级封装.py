# 导入更多必要的库
from sentence_transformers import CrossEncoder
from typing import List, Dict, Any
import torch

class BGEReranker:
    """BGE Reranker高级封装
    
    提供批量重排序、GPU加速、评估指标计算等高级功能
    """
    
    def __init__(self, model_name: str = "BAAI/bge-reranker-large"):
        # 检测是否有可用的GPU，有则使用GPU加速
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        # 创建CrossEncoder模型，指定设备
        self.model = CrossEncoder(model_name, device=self.device)
        self.model_name = model_name
        
        # 打印初始化信息
        print(f"[BGE Reranker] 模型: {model_name}")
        print(f"[BGE Reranker] 设备: {self.device}")
    
    def rerank_batch(
        self,
        queries: List[str],
        doc_lists: List[List[str]],
        top_k: int = 5,
        batch_size: int = 32
    ) -> List[List[Dict[str, Any]]]:
        """
        批量重排序
        
        一次性处理多个查询，提高吞吐量
        
        参数:
            queries: 查询列表
            doc_lists: 每个查询对应的文档列表（注意：长度需与queries一致）
            top_k: 每个查询返回的结果数
            batch_size: 批处理大小，用于控制GPU内存使用
        
        返回:
            每个查询的重排序结果列表
        """
        all_results = []  # 存储所有查询的结果
        
        # 遍历每个查询（可以优化为批量处理）
        for query, docs in zip(queries, doc_lists):
            # 空文档列表直接跳过，返回空结果
            if not docs:
                all_results.append([])
                continue
            
            # 构建查询-文档对
            # 格式: [(query, doc1), (query, doc2), ...]
            pairs = [(query, doc) for doc in docs]
            
            # 批量预测
            # predict()方法支持批量处理，batch_size控制每批大小
            # show_progress_bar=False隐藏进度条
            scores = self.model.predict(
                pairs,
                batch_size=batch_size,
                show_progress_bar=False
            )
            
            # 构建结果列表
            # 对分数排序，取top_k
            results = [
                {
                    "document": doc,        # 文档内容
                    "score": float(score),  # 相关性分数
                    "rank": i + 1           # 排名
                }
                for i, (doc, score) in enumerate(
                    # sorted()按分数降序排列
                    sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)[:top_k]
                )
            ]
            
            all_results.append(results)
        
        return all_results
    
    def compute_mrr(
        self,
        queries: List[str],
        doc_lists: List[List[str]],
        ground_truth_indices: List[int]
    ) -> float:
        """
        计算MRR (Mean Reciprocal Rank)
        
        评估重排序质量的常用指标
        
        MRR = 平均(1/第一个正确答案的排名)
        范围0-1，越接近1越好
        
        参数:
            queries: 查询列表
            doc_lists: 每个查询的候选文档列表
            ground_truth_indices: 每个查询对应的正确答案索引
        
        返回:
            MRR分数
        """
        rr_sum = 0.0  # 累计排名分数的倒数
        
        # 遍历每个查询
        for query, docs, gt_idx in zip(queries, doc_lists, ground_truth_indices):
            # 构建查询-文档对
            pairs = [(query, doc) for doc in docs]
            
            # 预测分数
            scores = self.model.predict(pairs)
            
            # 获取排序后的索引
            # argsort返回升序索引，[::-1]反转实现降序
            sorted_indices = np.argsort(scores)[::-1]
            
            # 找到ground truth在排序后的位置
            # np.where返回满足条件的索引数组
            rank = np.where(sorted_indices == gt_idx)[0]
            
            # 如果找到正确答案，计算排名分数的倒数
            # rank[0]是0-indexed，转为1-indexed
            if len(rank) > 0:
                rr_sum += 1.0 / (rank[0] + 1)
        
        # 返回平均MRR
        return rr_sum / len(queries)


# ============ RAG Pipeline集成 ============

class RAGWithRerank:
    """带重排序的RAG系统
    
    完整的RAG Pipeline：向量检索 + Cross-Encoder重排序
    """
    
    def __init__(
        self,
        embedding_model,
        reranker_model: str = "BAAI/bge-reranker-large",
        initial_k: int = 20,      # 初始检索数量
        final_k: int = 5          # 重排序后数量
    ):
        """
        初始化RAG系统
        
        参数:
            embedding_model: 向量编码模型名称或SentenceTransformer实例
            reranker_model: 重排序模型名称
            initial_k: 初始向量检索返回的候选数量
            final_k: 重排序后最终返回的数量
        """
        # 导入SentenceTransformer（延迟导入避免未安装时报错）
        from sentence_transformers import SentenceTransformer
        
        # 初始化向量编码模型
        self.embedding_model = SentenceTransformer(embedding_model)
        # 初始化Reranker
        self.reranker = BGEReranker(reranker_model)
        # 保存参数
        self.initial_k = initial_k
        self.final_k = final_k
        
        # 存储文档和对应的向量
        self.documents: List[str] = []
        self.embeddings: List[np.ndarray] = []
    
    def add_documents(self, docs: List[str]):
        """添加文档到知识库"""
        # 将新文档添加到列表
        self.documents.extend(docs)
        
        # 使用向量模型编码所有文档
        new_embeddings = self.embedding_model.encode(docs)
        # 将新向量添加到向量列表
        self.embeddings.extend(new_embeddings)
    
    def retrieve(self, query: str) -> List[Dict[str, Any]]:
        """
        检索（两阶段：向量检索 + 重排序）
        
        流程:
        1. 向量检索获取initial_k个候选
        2. Cross Encoder重排序
        3. 返回final_k个结果
        """
        import numpy as np
        
        # 空知识库直接返回空结果
        if not self.documents:
            return []
        
        # Stage 1: 向量检索（Bi-Encoder）
        # 将查询编码为向量
        query_emb = self.embedding_model.encode(query)
        
        # 计算查询向量与所有文档向量的相似度
        # 使用点积计算余弦相似度（需要归一化）
        similarities = [
            np.dot(query_emb, doc_emb) / (np.linalg.norm(query_emb) * np.linalg.norm(doc_emb))
            for doc_emb in self.embeddings
        ]
        
        # 获取Top-K候选索引
        # argsort返回升序，[::-1]反转实现降序
        top_k_indices = np.argsort(similarities)[-self.initial_k:][::-1]
        # 根据索引提取对应的文档
        candidates = [self.documents[i] for i in top_k_indices]
        
        # 打印日志
        print(f"[检索] 向量检索返回 {len(candidates)} 个候选")
        
        # Stage 2: 重排序（Cross Encoder）
        # 使用Reranker对候选文档进行精确排序
        reranked = self.reranker.rerank_batch(
            [query],              # 查询列表（单个查询）
            [candidates],        # 候选文档列表
            top_k=self.final_k    # 返回数量
        )[0]                      # 取第一个（因为只有一个查询）
        
        # 打印日志
        print(f"[检索] 重排序后返回 {len(reranked)} 个结果")
        
        return reranked


# ============ 完整示例 ============

def rag_with_rerank_example():
    """带重排序的RAG系统示例"""
    
    print("="*60)
    print("带重排序的RAG系统示例")
    print("="*60)
    
    # 初始化RAG系统
    # embedding_model: 使用BGE中文小模型
    # reranker_model: 使用BGE重排序基础版
    # initial_k: 初始检索20个候选
    # final_k: 最终返回3个结果
    rag = RAGWithRerank(
        embedding_model="BAAI/bge-small-zh",
        reranker_model="BAAI/bge-reranker-base",
        initial_k=10,
        final_k=3
    )
    
    # 添加文档到知识库
    documents = [
        "机器学习是人工智能的一个分支，通过数据训练模型来进行预测和决策。",
        "深度学习使用多层神经网络，是机器学习的一个重要子领域。",
        "自然语言处理（NLP）是人工智能的一个分支，专注于计算机理解和生成人类语言。",
        "计算机视觉使计算机能够从图像或视频中提取信息并理解视觉世界。",
        "强化学习通过与环境交互来学习最优行为策略，常用于游戏和机器人控制。",
        "监督学习需要标记数据进行训练，是最常见的机器学习方法。",
        "无监督学习从无标记数据中发现隐藏的模式和结构。",
        "迁移学习可以将一个任务中学到的知识应用到相关任务中。",
        "Python是数据科学和机器学习领域最受欢迎的编程语言。",
        "TensorFlow和PyTorch是两个最流行的深度学习框架。"
    ]
    
    # 添加文档
    rag.add_documents(documents)
    print(f"[系统] 已加载 {len(documents)} 篇文档")
    
    # 查询
    query = "机器学习和深度学习有什么区别？"
    print(f"\n查询: {query}")
    print("\n" + "-"*60)
    
    # 执行检索
    results = rag.retrieve(query)
    
    # 打印结果
    print("\n检索结果:")
    for i, result in enumerate(results, 1):
        print(f"\n{i}. [分数: {result['score']:.4f}]")
        print(f"   {result['document']}")
    
    print("\n" + "="*60)
    print("重排序优势:")
    print("- 相比纯向量检索，结果更精准")
    print("- Cross Encoder深度理解查询和文档关系")
    print("- 适合作为RAG Pipeline的第二阶段精排")


if __name__ == "__main__":
    rag_with_rerank_example()
