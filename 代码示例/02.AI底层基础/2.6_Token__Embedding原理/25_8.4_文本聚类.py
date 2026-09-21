from sklearn.cluster import KMeans
import numpy as np

class TextClusterer:
    """文本聚类"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
    
    def get_embeddings(self, texts):
        """获取文本嵌入"""
        encoded = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            output = self.model(**encoded)
        return output.last_hidden_state[:, 0, :].numpy()
    
    def cluster(self, texts, n_clusters=3):
        """KMeans聚类"""
        embeddings = self.get_embeddings(texts)
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        return labels

# 使用示例
clusterer = TextClusterer()
texts = [
    "机器学习算法",
    "深度神经网络",
    "足球比赛结果",
    "篮球运动介绍",
    "自然语言处理",
    "世界杯足球赛",
]

labels = clusterer.cluster(texts, n_clusters=2)
for text, label in zip(texts, labels):
    print(f"簇{label}: {text}")
