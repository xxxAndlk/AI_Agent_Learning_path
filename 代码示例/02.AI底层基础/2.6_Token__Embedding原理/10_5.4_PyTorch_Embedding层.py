import torch
import torch.nn as nn

# ========== 基础用法 ==========
vocab_size = 10000
embed_dim = 256

embedding = nn.Embedding(vocab_size, embed_dim)

# 查询
input_ids = torch.tensor([[1, 2, 3], [4, 5, 6]])  # (batch=2, seq_len=3)
output = embedding(input_ids)  # (batch=2, seq_len=3, embed_dim=256)

# ========== 带padding处理 ==========
# padding_idx: 指定哪个ID是填充，其梯度始终为0
embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)

# ========== 预训练权重加载 ==========
import numpy as np

# 假设有预训练的词向量
pretrained_vectors = np.load("word2vec.npy")  # (vocab_size, embed_dim)

embedding = nn.Embedding(vocab_size, embed_dim)
embedding.weight.data.copy_(torch.from_numpy(pretrained_vectors))

# 可选：冻结预训练权重
embedding.weight.requires_grad = False
