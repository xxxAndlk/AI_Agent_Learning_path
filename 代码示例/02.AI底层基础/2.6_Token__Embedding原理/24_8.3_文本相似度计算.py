class TextSimilarity:
    """文本相似度计算器"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
    
    def get_embedding(self, text):
        """获取文本嵌入（使用[CLS]向量）"""
        encoded = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            output = self.model(**encoded)
        return output.last_hidden_state[:, 0, :]  # [CLS]向量
    
    def cosine_similarity(self, text1, text2):
        """计算两个文本的余弦相似度"""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)
        return F.cosine_similarity(emb1, emb2).item()
    
    def semantic_similarity_matrix(self, texts):
        """计算文本集合的相似度矩阵"""
        encoded = self.tokenizer(texts, padding=True, return_tensors="pt")
        with torch.no_grad():
            output = self.model(**encoded)
        embeddings = output.last_hidden_state[:, 0, :]  # (n, dim)
        
        # 归一化后点积 = 余弦相似度
        embeddings = F.normalize(embeddings, p=2, dim=1)
        similarity_matrix = torch.matmul(embeddings, embeddings.T)
        return similarity_matrix

# 使用示例
similarity = TextSimilarity()

# 计算文本对相似度
text1 = "我喜欢吃苹果"
text2 = "我喜欢吃水果"
text3 = "今天天气很好"

score1 = similarity.cosine_similarity(text1, text2)  # 高相似度
score2 = similarity.cosine_similarity(text1, text3)  # 低相似度
print(f"'{text1}' vs '{text2}': {score1:.4f}")
print(f"'{text1}' vs '{text3}': {score2:.4f}")

# 批量相似度矩阵
texts = ["机器学习很有趣", "深度学习很强大", "今天天气真好"]
matrix = similarity.semantic_similarity_matrix(texts)
print("\n相似度矩阵:")
for i, t1 in enumerate(texts):
    for j, t2 in enumerate(texts):
        print(f"{matrix[i,j]:.3f}", end=" ")
    print()
