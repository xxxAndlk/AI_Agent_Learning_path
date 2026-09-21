from typing import List, Dict, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer, util

class RAGEvaluator:
    """RAG系统评测器"""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('BAAI/bge-large-zh')
    
    def evaluate_retrieval(
        self, 
        queries: List[str], 
        retrieved_docs: List[List[str]], 
        ground_truth_docs: List[List[str]]
    ) -> Dict[str, float]:
        """评测检索质量
        
        参数:
            queries: 查询列表
            retrieved_docs: 每个查询检索到的文档列表
            ground_truth_docs: 每个查询的真实相关文档列表
        """
        metrics = {"recall@1": [], "recall@3": [], "recall@5": [], "mrr": []}
        
        for query, retrieved, ground_truth in zip(queries, retrieved_docs, ground_truth_docs):
            # 计算Recall@K
            for k in [1, 3, 5]:
                retrieved_k = set(retrieved[:k])
                ground_truth_set = set(ground_truth)
                recall = len(retrieved_k & ground_truth_set) / len(ground_truth_set) if ground_truth_set else 0
                metrics[f"recall@{k}"].append(recall)
            
            # 计算MRR (Mean Reciprocal Rank)
            mrr = 0
            for i, doc in enumerate(retrieved):
                if doc in ground_truth:
                    mrr = 1 / (i + 1)
                    break
            metrics["mrr"].append(mrr)
        
        # 计算平均值
        return {k: np.mean(v) for k, v in metrics.items()}
    
    def evaluate_answer_faithfulness(
        self, 
        answers: List[str], 
        contexts: List[str]
    ) -> List[float]:
        """评测答案忠实度
        
        通过对比答案和上下文的语义相似度来评估
        """
        faithfulness_scores = []
        
        for answer, context in zip(answers, contexts):
            # 编码
            answer_emb = self.embedding_model.encode(answer, convert_to_tensor=True)
            context_emb = self.embedding_model.encode(context, convert_to_tensor=True)
            
            # 计算相似度
            similarity = util.pytorch_cos_sim(answer_emb, context_emb).item()
            faithfulness_scores.append(similarity)
        
        return faithfulness_scores
    
    def evaluate_answer_relevance(
        self, 
        queries: List[str], 
        answers: List[str]
    ) -> List[float]:
        """评测答案相关性"""
        relevance_scores = []
        
        for query, answer in zip(queries, answers):
            query_emb = self.embedding_model.encode(query, convert_to_tensor=True)
            answer_emb = self.embedding_model.encode(answer, convert_to_tensor=True)
            
            similarity = util.pytorch_cos_sim(query_emb, answer_emb).item()
            relevance_scores.append(similarity)
        
        return relevance_scores
    
    def comprehensive_evaluation(
        self,
        test_cases: List[Dict]
    ) -> Dict[str, Any]:
        """综合评测"""
        results = {
            "retrieval": {},
            "generation": {},
            "overall": {}
        }
        
        # 提取数据
        queries = [case["query"] for case in test_cases]
        retrieved = [case["retrieved_docs"] for case in test_cases]
        ground_truth = [case["ground_truth_docs"] for case in test_cases]
        answers = [case["answer"] for case in test_cases]
        contexts = [case["context"] for case in test_cases]
        
        # 检索评测
        results["retrieval"] = self.evaluate_retrieval(queries, retrieved, ground_truth)
        
        # 生成评测
        results["generation"]["faithfulness"] = np.mean(
            self.evaluate_answer_faithfulness(answers, contexts)
        )
        results["generation"]["relevance"] = np.mean(
            self.evaluate_answer_relevance(queries, answers)
        )
        
        # 综合得分
        results["overall"]["score"] = (
            results["retrieval"]["recall@3"] * 0.4 +
            results["generation"]["faithfulness"] * 0.3 +
            results["generation"]["relevance"] * 0.3
        )
        
        return results


def run_rag_evaluation_example():
    """RAG评测示例"""
    evaluator = RAGEvaluator()
    
    # 测试用例
    test_cases = [
        {
            "query": "什么是RAG？",
            "retrieved_docs": [
                "RAG是检索增强生成的缩写",
                "RAG结合检索和生成技术",
                "其他无关文档"
            ],
            "ground_truth_docs": [
                "RAG是检索增强生成的缩写",
                "RAG结合检索和生成技术"
            ],
            "answer": "RAG（Retrieval-Augmented Generation）是一种结合检索和生成的技术...",
            "context": "RAG是检索增强生成的缩写，结合了信息检索和文本生成..."
        }
    ]
    
    results = evaluator.comprehensive_evaluation(test_cases)
    
    print("\n" + "="*50)
    print("RAG评测结果")
    print("="*50)
    print(f"检索 - Recall@3: {results['retrieval']['recall@3']:.2%}")
    print(f"生成 - 忠实度: {results['generation']['faithfulness']:.2%}")
    print(f"生成 - 相关性: {results['generation']['relevance']:.2%}")
    print(f"综合得分: {results['overall']['score']:.2%}")


if __name__ == "__main__":
    run_rag_evaluation_example()
