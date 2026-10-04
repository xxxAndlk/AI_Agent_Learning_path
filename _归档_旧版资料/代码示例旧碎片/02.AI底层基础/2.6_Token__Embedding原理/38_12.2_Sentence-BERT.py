from sentence_transformers import SentenceTransformer
import numpy as np

# 加载预训练模型
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 单句编码
sentence = "深度学习是人工智能的核心技术"
embedding = model.encode(sentence)

print(f"句子: {sentence}")
print(f"嵌入维度: {embedding.shape}")
print(f"嵌入示例: {embedding[:5]}")

# 批量编码
sentences = [
    "深度学习是人工智能的核心技术",
    "机器学习是AI的一个分支",
    "今天天气真好",
    "我喜欢踢足球",
]

embeddings = model.encode(sentences)
print(f"\n批量编码形状: {embeddings.shape}")

# 计算相似度
from sklearn.metrics.pairwise import cosine_similarity

similarity_matrix = cosine_similarity(embeddings)
print("\n相似度矩阵:")
for i, s1 in enumerate(sentences):
    for j, s2 in enumerate(sentences):
        print(f"  {i} vs {j}: {similarity_matrix[i,j]:.3f}")
