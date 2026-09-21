from openai import OpenAI
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import math

client = OpenAI()

@dataclass
class Example:
    """示例数据类"""
    input: str
    output: str
    embedding: Optional[List[float]] = None
    cluster_id: Optional[int] = None


class FewShotSelector:
    """Few-shot示例选择器
    
    实现多种示例选择策略
    """
    
    def __init__(self, client: OpenAI):
        """初始化选择器"""
        self.client = client
        self.examples: List[Example] = []
    
    def add_example(self, example: Example) -> None:
        """添加示例到候选池"""
        self.examples.append(example)
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的embedding"""
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def compute_similarity(
        self, 
        text1: str, 
        text2: str
    ) -> float:
        """计算两个文本的余弦相似度
        
        Args:
            text1: 第一个文本
            text2: 第二个文本
            
        Returns:
            相似度分数（-1到1）
        """
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        norm1 = math.sqrt(sum(a * a for a in emb1))
        norm2 = math.sqrt(sum(b * b for b in emb2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def similarity_based_select(
        self, 
        query: str, 
        k: int = 3
    ) -> List[Example]:
        """基于相似性选择示例
        
        选择与查询最相似的k个示例
        
        Args:
            query: 当前查询
            k: 选择数量
            
        Returns:
            选中的示例列表
        """
        # 计算每个示例与查询的相似度
        similarities = []
        for example in self.examples:
            sim = self.compute_similarity(query, example.input)
            similarities.append((example, sim))
        
        # 按相似度降序排序
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # 返回top-k
        return [ex for ex, _ in similarities[:k]]
    
    def diversity_based_select(
        self, 
        k: int = 3
    ) -> List[Example]:
        """基于多样性选择示例
        
        使用聚类确保选择多样化的示例
        
        Args:
            k: 选择数量
            
        Returns:
            选中的示例列表
        """
        if len(self.examples) <= k:
            return self.examples
        
        # 为所有示例计算embedding
        for ex in self.examples:
            if ex.embedding is None:
                ex.embedding = self.get_embedding(ex.input)
        
        # 简单聚类：使用k-means的简化版
        clusters = self._kmeans_clustering(k)
        
        selected = []
        for cluster_id, cluster_examples in clusters.items():
            if cluster_examples:
                # 选择每个聚类中第一个作为代表
                selected.append(cluster_examples[0])
        
        return selected[:k]
    
    def _kmeans_clustering(
        self, 
        k: int
    ) -> Dict[int, List[Example]]:
        """简化的K-means聚类"""
        # 随机选择k个中心
        centers = random.sample(self.examples, min(k, len(self.examples)))
        center_embeddings = [ex.embedding for ex in centers]
        
        # 分配到最近的中心
        clusters = {i: [] for i in range(k)}
        
        for ex in self.examples:
            if ex.embedding is None:
                continue
            
            similarities = [
                self._cosine_sim(ex.embedding, ce) 
                for ce in center_embeddings
            ]
            cluster_id = similarities.index(max(similarities))
            clusters[cluster_id].append(ex)
        
        return clusters
    
    def _cosine_sim(
        self, 
        a: List[float], 
        b: List[float]
    ) -> float:
        """计算余弦相似度"""
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        return dot / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
    
    def hybrid_select(
        self, 
        query: str, 
        k: int = 3,
        similarity_weight: float = 0.6
    ) -> List[Example]:
        """混合选择策略
        
        结合相似性和多样性
        
        Args:
            query: 当前查询
            k: 选择数量
            similarity_weight: 相似性权重
            
        Returns:
            选中的示例列表
        """
        if not self.examples:
            return []
        
        # 第一步：基于相似性筛选候选
        candidate_pool_size = min(k * 3, len(self.examples))
        similar_examples = self.similarity_based_select(query, candidate_pool_size)
        
        # 第二步：从中选择多样化的子集
        # 使用MMR（最大边际相关）准则
        selected = []
        remaining = similar_examples.copy()
        
        for _ in range(k):
            if not remaining:
                break
            
            best_score = -float('inf')
            best_example = remaining[0]
            
            for ex in remaining:
                # 与查询的相似度
                sim_to_query = self.compute_similarity(query, ex.input)
                
                # 与已选示例的最大相似度（多样性惩罚）
                max_sim_to_selected = 0
                if selected:
                    sims = [
                        self.compute_similarity(ex.input, s.input) 
                        for s in selected
                    ]
                    max_sim_to_selected = max(sims)
                
                # MMR分数
                mmr_score = similarity_weight * sim_to_query - \
                           (1 - similarity_weight) * max_sim_to_selected
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_example = ex
            
            selected.append(best_example)
            remaining.remove(best_example)
        
        return selected
    
    def build_prompt(
        self, 
        query: str, 
        examples: List[Example],
        include_instruction: bool = True
    ) -> str:
        """构建few-shot提示
        
        Args:
            query: 用户查询
            examples: 选中的示例
            include_instruction: 是否包含任务指令
            
        Returns:
            完整的提示字符串
        """
        parts = []
        
        if include_instruction:
            parts.append("请根据以下示例完成任务：")
        
        # 添加示例
        for ex in examples:
            parts.append(f"输入: {ex.input}")
            parts.append(f"输出: {ex.output}")
            parts.append("")
        
        # 添加查询
        parts.append(f"输入: {query}")
        parts.append("输出:")
        
        return "\n".join(parts)


# 使用示例
def fewshot_selection_example():
    """Few-shot选择示例"""
    
    selector = FewShotSelector(client=client)
    
    # 添加候选示例
    examples_data = [
        ("今天天气很好", "The weather is nice today"),
        ("我喜欢学习中文", "I like learning Chinese"),
        ("这是一个苹果", "This is an apple"),
        ("明天要开会", "Tomorrow there is a meeting"),
        ("他在图书馆看书", "He is reading in the library"),
    ]
    
    for inp, out in examples_data:
        selector.add_example(Example(input=inp, output=out))
    
    query = "她在学校学习"
    
    # 相似性选择
    sim_selected = selector.similarity_based_select(query, k=2)
    print("相似性选择:")
    for ex in sim_selected:
        print(f"  {ex.input} -> {ex.output}")
    
    # 多样性选择
    div_selected = selector.diversity_based_select(k=3)
    print("\n多样性选择:")
    for ex in div_selected:
        print(f"  {ex.input} -> {ex.output}")
    
    # 混合选择
    hybrid_selected = selector.hybrid_select(query, k=3)
    print("\n混合选择:")
    for ex in hybrid_selected:
        print(f"  {ex.input} -> {ex.output}")
    
    # 构建提示
    prompt = selector.build_prompt(query, hybrid_selected)
    print(f"\n构建的提示:\n{prompt}")
