from sentence_transformers import SentenceTransformer
from sentence_transformers.models import Transformer, Pooling
from sentence_transformers import InputExample
from sentence_transformers import losses
from torch import nn

class CustomSentenceTransformer(nn.Module):
    """自定义Sentence Transformer"""
    
    def __init__(
        self,
        model_name: str = 'bert-base-chinese',
        pooling_mode: str = 'mean',
        max_seq_length: int = 256
    ):
        """
        初始化自定义模型
        
        参数:
            model_name: 预训练模型名称
            pooling_mode: 池化模式 ('mean', 'cls', 'max')
            max_seq_length: 最大序列长度
        """
        super().__init__()
        
        # 使用SentenceTransformer库
        self.model = SentenceTransformer(model_name)
        self.model.max_seq_length = max_seq_length
        self.pooling_mode = pooling_mode
    
    def encode(
        self,
        sentences,
        batch_size: int = 32,
        show_progress: bool = False,
        normalize: bool = True
    ):
        """
        编码句子
        
        参数:
            sentences: 句子列表
            batch_size: 批量大小
            show_progress: 是否显示进度条
            normalize: 是否归一化向量
        
        返回:
            句子嵌入向量
        """
        embeddings = self.model.encode(
            sentences,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            normalize_embeddings=normalize
        )
        
        return embeddings
    
    def encode_pair(
        self,
        sentence1,
        sentence2,
        show_progress: bool = False
    ):
        """
        编码句子对
        
        参数:
            sentence1: 第一个句子
            sentence2: 第二个句子
            show_progress: 是否显示进度条
        
        返回:
            句子对嵌入
        """
        embeddings = self.model.encode(
            [sentence1, sentence2],
            show_progress_bar=show_progress
        )
        
        return embeddings[0], embeddings[1]
    
    def compute_similarity(self, sentence1, sentence2):
        """
        计算两个句子的相似度
        
        参数:
            sentence1: 第一个句子
            sentence2: 第二个句子
        
        返回:
            相似度分数
        """
        import numpy as np
        
        embeddings = self.model.encode([sentence1, sentence2])
        
        # 归一化后计算点积即为余弦相似度
        embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        
        similarity = np.dot(embeddings[0], embeddings[1])
        
        return similarity
