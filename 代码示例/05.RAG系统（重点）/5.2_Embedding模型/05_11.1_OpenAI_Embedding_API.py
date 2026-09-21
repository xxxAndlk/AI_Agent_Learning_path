from openai import OpenAI
from typing import List, Dict, Any

class OpenAIEmbedder:
    """OpenAI Embedding封装类"""
    
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimensions: int = None
    ):
        """
        初始化OpenAI Embedding
        
        参数:
            api_key: API密钥
            model: 模型名称
            dimensions: 嵌入维度（仅text-embedding-3支持）
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = dimensions
    
    def embed_text(self, text: str) -> List[float]:
        """
        获取单个文本的嵌入向量
        
        参数:
            text: 输入文本
        
        返回:
            嵌入向量
        """
        # dimensions仅在显式指定时传参，避免发送null导致API报错
        response = self.client.embeddings.create(
            model=self.model,
            input=text,
            **({"dimensions": self.dimensions} if self.dimensions else {})
        )
        
        return response.data[0].embedding
    
    def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 100
    ) -> List[List[float]]:
        """
        批量获取嵌入向量
        
        参数:
            texts: 文本列表
            batch_size: 批量大小
        
        返回:
            嵌入向量列表
        """
        embeddings = []
        
        # 分批处理
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            response = self.client.embeddings.create(
                model=self.model,
                input=batch,
                **({"dimensions": self.dimensions} if self.dimensions else {})
            )
            
            batch_embeddings = [data.embedding for data in response.data]
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        计算两个文本的相似度
        
        参数:
            text1: 第一个文本
            text2: 第二个文本
        
        返回:
            相似度分数
        """
        import numpy as np
        
        embed1 = self.embed_text(text1)
        embed2 = self.embed_text(text2)
        
        # 计算余弦相似度
        dot_product = sum(a * b for a, b in zip(embed1, embed2))
        norm1 = sum(a * a for a in embed1) ** 0.5
        norm2 = sum(b * b for b in embed2) ** 0.5
        
        similarity = dot_product / (norm1 * norm2)
        
        return similarity
