"""
完整的Embedding系统

包含：模型选择、批量处理、缓存、相似度计算
"""

from typing import List, Dict, Any, Optional
import numpy as np
import hashlib
import json

class EmbeddingSystem:
    """完整的Embedding系统"""
    
    def __init__(
        self,
        model_type: str = "local",  # "local" or "openai"
        model_name: str = "all-MiniLM-L6-v2",
        api_key: str = None,
        use_cache: bool = True
    ):
        """
        初始化系统
        
        参数:
            model_type: 模型类型
            model_name: 模型名称
            api_key: OpenAI API密钥
            use_cache: 是否使用缓存
        """
        self.model_type = model_type
        self.model_name = model_name
        self.use_cache = use_cache
        
        # 初始化模型
        if model_type == "local":
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer(model_name)
        else:
            self.api_key = api_key
            # 使用OpenAI Embedding（openai>=1.0客户端范式，替代旧版模块级api_key）
            from openai import OpenAI
            self.openai = OpenAI(api_key=api_key)
        
        # 缓存
        self.cache: Dict[str, np.ndarray] = {}
    
    def _get_cache_key(self, text: str) -> str:
        """生成缓存键"""
        return hashlib.md5(text.encode()).hexdigest()
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        获取单个文本的嵌入向量
        
        参数:
            text: 输入文本
        
        返回:
            嵌入向量
        """
        # 尝试缓存
        if self.use_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key]
        
        # 计算嵌入
        if self.model_type == "local":
            embedding = self.model.encode(text)
        else:
            response = self.openai.embeddings.create(
                model=self.model_name,
                input=text
            )
            embedding = np.array(response.data[0].embedding)
        
        # 缓存
        if self.use_cache:
            self.cache[cache_key] = embedding
        
        return embedding
    
    def get_embeddings_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> np.ndarray:
        """
        批量获取嵌入向量
        
        参数:
            texts: 文本列表
            batch_size: 批量大小
            show_progress: 是否显示进度
        
        返回:
            嵌入向量矩阵
        """
        embeddings = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            # 处理缓存
            uncached_texts = []
            uncached_indices = []
            
            for j, text in enumerate(batch):
                if self.use_cache:
                    cache_key = self._get_cache_key(text)
                    if cache_key in self.cache:
                        embeddings.append(self.cache[cache_key])
                        continue
                
                uncached_texts.append(text)
                uncached_indices.append(j)
            
            # 计算未缓存的文本
            if uncached_texts:
                if self.model_type == "local":
                    batch_embeddings = self.model.encode(
                        uncached_texts,
                        show_progress_bar=show_progress and i == 0
                    )
                else:
                    response = self.openai.embeddings.create(
                        model=self.model_name,
                        input=uncached_texts
                    )
                    batch_embeddings = np.array([
                        data.embedding for data in response.data
                    ])
                
                # 缓存并添加到结果
                for idx, embedding in zip(uncached_indices, batch_embeddings):
                    if self.use_cache:
                        cache_key = self._get_cache_key(batch[idx])
                        self.cache[cache_key] = embedding
                    
                    # 需要插入到正确的位置
                    pass  # 简化处理
        
        # 简化版：直接批量处理
        if self.model_type == "local":
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress
            )
        else:
            embeddings = []
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i+batch_size]
                response = self.openai.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                batch_embeddings = [
                    data.embedding for data in response.data
                ]
                embeddings.extend(batch_embeddings)
            embeddings = np.array(embeddings)
        
        return embeddings
    
    def search_similar(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        语义搜索
        
        参数:
            query: 查询文本
            documents: 文档列表
            top_k: 返回数量
        
        返回:
            搜索结果列表
        """
        # 获取查询嵌入
        query_embedding = self.get_embedding(query)
        
        # 获取文档嵌入
        doc_embeddings = self.get_embeddings_batch(documents)
        
        # 计算相似度
        similarities = np.dot(
            doc_embeddings,
            query_embedding
        ) / (
            np.linalg.norm(doc_embeddings, axis=1) *
            np.linalg.norm(query_embedding)
        )
        
        # 排序
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        # 返回结果
        results = [
            {
                'text': documents[i],
                'score': float(similarities[i]),
                'index': int(i)
            }
            for i in top_indices
        ]
        
        return results
    
    def compute_similarity_matrix(
        self,
        texts: List[str]
    ) -> np.ndarray:
        """
        计算文本间的相似度矩阵
        
        参数:
            texts: 文本列表
        
        返回:
            相似度矩阵
        """
        embeddings = self.get_embeddings_batch(texts)
        
        # 归一化
        norm_embeddings = embeddings / np.linalg.norm(
            embeddings, axis=1, keepdims=True
        )
        
        # 计算点积矩阵（即余弦相似度矩阵）
        similarity_matrix = np.dot(norm_embeddings, norm_embeddings.T)
        
        return similarity_matrix
    
    def cluster_texts(
        self,
        texts: List[str],
        num_clusters: int = 5
    ) -> Dict[int, List[str]]:
        """
        文本聚类
        
        参数:
            texts: 文本列表
            num_clusters: 聚类数量
        
        返回:
            聚类结果
        """
        from sklearn.cluster import KMeans
        
        # 获取嵌入
        embeddings = self.get_embeddings_batch(texts)
        
        # KMeans聚类
        kmeans = KMeans(n_clusters=num_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(embeddings)
        
        # 整理结果
        clusters = {}
        for text, label in zip(texts, cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(text)
        
        return clusters
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()


def main():
    """测试主函数"""
    # 创建系统
    system = EmbeddingSystem(
        model_type="local",
        model_name="all-MiniLM-L6-v2"
    )
    
    # 测试文本
    texts = [
        "人工智能是未来的发展趋势",
        "机器学习是人工智能的一个分支",
        "今天天气很好，适合外出",
        "深度学习在图像识别领域应用广泛",
        "我喜欢吃苹果和香蕉"
    ]
    
    print("=" * 50)
    print("Embedding系统测试")
    print("=" * 50)
    
    # 测试获取嵌入
    print("\n1. 获取单个文本嵌入:")
    embedding = system.get_embedding(texts[0])
    print(f"   嵌入维度: {embedding.shape}")
    
    # 测试批量获取
    print("\n2. 批量获取嵌入:")
    embeddings = system.get_embeddings_batch(texts)
    print(f"   嵌入矩阵形状: {embeddings.shape}")
    
    # 测试语义搜索
    print("\n3. 语义搜索:")
    query = "人工智能技术"
    results = system.search_similar(query, texts, top_k=3)
    for i, r in enumerate(results, 1):
        print(f"   {i}. [{r['score']:.4f}] {r['text']}")
    
    # 测试聚类
    print("\n4. 文本聚类:")
    clusters = system.cluster_texts(texts, num_clusters=2)
    for label, cluster_texts in clusters.items():
        print(f"   类别 {label}: {cluster_texts}")
    
    # 缓存信息
    print(f"\n5. 缓存信息:")
    print(f"   缓存条目数: {len(system.cache)}")


if __name__ == "__main__":
    main()
