import torch.nn.functional as F

def cosine_similarity(vec1, vec2):
    """
    cos(θ) = (A·B) / (|A| × |B|)
    范围: [-1, 1]
    - 1: 方向相同（最相似）
    - 0: 正交（无关）
    - -1: 方向相反（最不相似）
    """
    return F.cosine_similarity(vec1.unsqueeze(0), vec2.unsqueeze(0))

# 示例
emb_猫 = torch.tensor([0.8, 0.2, 0.1])
emb_狗 = torch.tensor([0.7, 0.3, 0.2])
emb_汽车 = torch.tensor([-0.1, 0.9, 0.5])

similarity_猫狗 = cosine_similarity(emb_猫, emb_狗)    # ~0.95 高相似
similarity_猫汽车 = cosine_similarity(emb_猫, emb_汽车)  # ~0.3 低相似
