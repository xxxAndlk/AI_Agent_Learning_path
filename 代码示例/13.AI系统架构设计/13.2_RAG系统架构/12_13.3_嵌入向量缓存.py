import numpy as np
class EmbeddingCache:
    """嵌入向量缓存"""
    
    def __init__(self, max_size: int = 5000):
        """
        初始化嵌入缓存
        
        参数:
            max_size: 最大缓存数量
        """
        self.cache: Dict[str, np.ndarray] = {}
        self.max_size = max_size
    
    def _hash_text(self, text: str) -> str:
        """生成文本哈希"""
        return hashlib.sha256(text.encode()).hexdigest()
    
    def get(self, text: str) -> Optional[np.ndarray]:
        """
        获取嵌入向量
        
        参数:
            text: 文本
        
        返回:
            嵌入向量或None
        """
        text_hash = self._hash_text(text)
        return self.cache.get(text_hash)
    
    def set(self, text: str, embedding: np.ndarray):
        """
        缓存嵌入向量
        
        参数:
            text: 文本
            embedding: 嵌入向量
        """
        text_hash = self._hash_text(text)
        
        # 如果缓存已满，随机删除一项
        if len(self.cache) >= self.max_size:
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        self.cache[text_hash] = embedding
    
    def clear(self):
        """清空缓存"""
        self.cache.clear()
