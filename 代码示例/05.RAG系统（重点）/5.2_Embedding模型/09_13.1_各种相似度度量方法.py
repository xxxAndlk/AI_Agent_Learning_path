import numpy as np
from typing import List, Union

class SimilarityCalculator:
    """相似度计算器"""
    
    @staticmethod
    def cosine_similarity(
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        余弦相似度
        
        公式: (A·B) / (||A|| × ||B||)
        
        适用于：归一化后的向量，高维稀疏向量
        """
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    @staticmethod
    def euclidean_distance(
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        欧氏距离
        
        公式: sqrt(sum((A-B)^2))
        
        适用于：低维连续向量，聚类分析
        """
        return np.linalg.norm(vec1 - vec2)
    
    @staticmethod
    def manhattan_distance(
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        曼哈顿距离（城市距离）
        
        公式: sum(|A-B|)
        
        适用于：高维稀疏数据
        """
        return np.sum(np.abs(vec1 - vec2))
    
    @staticmethod
    def dot_product(
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        点积（内积）
        
        适用于：已归一化的向量
        """
        return np.dot(vec1, vec2)
    
    @staticmethod
    def pearson_correlation(
        vec1: np.ndarray,
        vec2: np.ndarray
    ) -> float:
        """
        皮尔逊相关系数
        
        衡量线性相关性，范围[-1, 1]
        """
        return np.corrcoef(vec1, vec2)[0, 1]
    
    @staticmethod
    def batch_cosine_similarity(
        vectors: np.ndarray,
        query: np.ndarray
    ) -> np.ndarray:
        """
        批量计算余弦相似度
        
        参数:
            vectors: 向量矩阵 (N, D)
            query: 查询向量 (D,)
        
        返回:
            相似度数组 (N,)
        """
        # 归一化
        vectors_norm = vectors / np.linalg.norm(vectors, axis=1, keepdims=True)
        query_norm = query / np.linalg.norm(query)
        
        # 计算
        similarities = np.dot(vectors_norm, query_norm)
        
        return similarities


def similarity_use_cases():
    """相似度计算使用场景对比"""
    
    # 示例向量
    vec_a = np.array([1.0, 2.0, 3.0])
    vec_b = np.array([2.0, 4.0, 6.0])
    vec_c = np.array([3.0, 2.0, 1.0])
    
    print("=" * 50)
    print("相似度计算对比")
    print("=" * 50)
    
    # 余弦相似度
    cos_ab = SimilarityCalculator.cosine_similarity(vec_a, vec_b)
    cos_ac = SimilarityCalculator.cosine_similarity(vec_a, vec_c)
    print(f"\n余弦相似度:")
    print(f"  A-B (方向相同，尺度不同): {cos_ab:.4f}")
    print(f"  A-C (方向不同): {cos_ac:.4f}")
    
    # 欧氏距离
    euc_ab = SimilarityCalculator.euclidean_distance(vec_a, vec_b)
    euc_ac = SimilarityCalculator.euclidean_distance(vec_a, vec_c)
    print(f"\n欧氏距离:")
    print(f"  A-B: {euc_ab:.4f}")
    print(f"  A-C: {euc_ac:.4f}")
    
    # 点积（需要归一化）
    vec_a_norm = vec_a / np.linalg.norm(vec_a)
    vec_b_norm = vec_b / np.linalg.norm(vec_b)
    vec_c_norm = vec_c / np.linalg.norm(vec_c)
    
    dot_ab = np.dot(vec_a_norm, vec_b_norm)
    dot_ac = np.dot(vec_a_norm, vec_c_norm)
    print(f"\n点积（归一化后）:")
    print(f"  A-B: {dot_ab:.4f}")
    print(f"  A-C: {dot_ac:.4f}")
