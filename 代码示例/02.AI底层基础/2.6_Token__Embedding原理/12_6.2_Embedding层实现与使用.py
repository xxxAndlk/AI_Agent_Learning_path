import torch                        # PyTorch核心库
import torch.nn as nn               # 神经网络模块

class TextEmbedding(nn.Module):
    """文本嵌入层：结合词嵌入和位置嵌入
    
    Transformer模型中，输入需要同时包含语义信息（词嵌入）和位置信息（位置嵌入）
    
    为什么需要位置嵌入？
    - Self-Attention是置换不变的：打乱输入顺序，输出只是顺序对应改变
    - 模型无法感知"猫吃鱼"和"鱼吃猫"的区别
    - 位置嵌入为每个位置提供唯一的位置编码
    """
    def __init__(self, vocab_size, embed_dim, max_seq_len=512):
        """
        参数:
            vocab_size: 词汇表大小（不同token的总数）
            embed_dim: 嵌入维度（如BERT为768）
            max_seq_len: 最大序列长度（BERT为512）
        """
        super().__init__()
        # 词嵌入层：将token ID映射为稠密向量
        # vocab_size个token，每个token对应embed_dim维向量
        # 参数量 = vocab_size × embed_dim
        # BERT-base: 30522 × 768 ≈ 23.4M参数
        self.token_embedding = nn.Embedding(vocab_size, embed_dim)
        
        # 位置嵌入层：将位置索引映射为稠密向量
        # 让模型感知token在序列中的位置
        # 参数量 = max_seq_len × embed_dim
        # BERT-base: 512 × 768 ≈ 0.4M参数
        self.position_embedding = nn.Embedding(max_seq_len, embed_dim)
    
    def forward(self, input_ids):
        """前向传播
        
        参数:
            input_ids: token ID张量 (batch_size, seq_len)
        返回:
            词嵌入 + 位置嵌入的总和 (batch_size, seq_len, embed_dim)
        """
        batch_size, seq_len = input_ids.shape  # 获取batch大小和序列长度
        
        # 生成位置索引：[[0, 1, 2, ..., seq_len-1], [0, 1, 2, ...], ...]
        # torch.arange(seq_len): 生成 [0, 1, 2, ..., seq_len-1]
        # .unsqueeze(0): 从(seq_len,)变为(1, seq_len)，增加batch维度
        # .repeat(batch_size, 1): 复制batch_size次，变为(batch_size, seq_len)
        # device=input_ids.device: 确保在同一设备上（CPU/GPU）
        position_ids = torch.arange(seq_len, device=input_ids.device).unsqueeze(0).repeat(batch_size, 1)
        
        # 词嵌入：每个token ID查表得到向量
        # 输入: (batch_size, seq_len) 的整数索引
        # 输出: (batch_size, seq_len, embed_dim) 的浮点向量
        token_emb = self.token_embedding(input_ids)
        
        # 位置嵌入：每个位置索引查表得到向量
        # 输入: (batch_size, seq_len) 的位置索引
        # 输出: (batch_size, seq_len, embed_dim) 的位置向量
        pos_emb = self.position_embedding(position_ids)
        
        # 最终嵌入 = 词嵌入 + 位置嵌入
        # 两者相加使模型同时获得语义和位置信息
        # 为什么可以相加？
        # - 维度相同，数学上可行
        # - 类似于傅里叶级数：信号 = 基信号的叠加
        # - 位置信息作为"偏置"融入语义向量
        return token_emb + pos_emb

if __name__ == "__main__":
    # BERT-base配置
    vocab_size = 30522                # 词汇表大小
    embed_dim = 768                   # 嵌入维度
    
    # 创建嵌入层
    embedding_layer = TextEmbedding(vocab_size, embed_dim)
    
    # 创建随机输入：batch_size=32, seq_len=10
    # 模拟32个样本，每个样本10个token
    input_ids = torch.randint(0, vocab_size, (32, 10))
    
    # 前向传播
    embeddings = embedding_layer(input_ids)
    
    print("Embedding输出形状:", embeddings.shape)
    # 输出: torch.Size([32, 10, 768])
    # 表示32个样本，每个样本10个token，每个token是768维向量
    
    # 计算参数量
    total_params = sum(p.numel() for p in embedding_layer.parameters())
    print(f"总参数量: {total_params:,}")
    # 输出: 总参数量: 23,838,720
