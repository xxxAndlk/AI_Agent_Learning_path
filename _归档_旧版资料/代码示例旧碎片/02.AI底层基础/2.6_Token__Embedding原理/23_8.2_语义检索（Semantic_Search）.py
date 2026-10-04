import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

class SemanticSearch:
    """语义检索引擎"""
    
    def __init__(self, model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.index = None  # 文档向量索引
    
    def _mean_pooling(self, model_output, attention_mask):
        """平均池化：将token嵌入聚合为句子嵌入"""
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.shape).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def encode(self, texts):
        """编码文本为向量"""
        encoded = self.tokenizer(texts, padding=True, truncation=True, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**encoded)
        embeddings = self._mean_pooling(outputs, encoded["attention_mask"])
        return F.normalize(embeddings, p=2, dim=1)  # L2归一化
    
    def index_documents(self, documents):
        """索引文档库"""
        self.documents = documents
        self.index = self.encode(documents)
    
    def search(self, query, top_k=5):
        """搜索最相似的文档"""
        query_vec = self.encode([query])
        # 计算余弦相似度
        similarities = torch.matmul(query_vec, self.index.T).squeeze()
        # 获取top_k索引
        top_indices = torch.topk(similarities, top_k).indices.tolist()
        return [(self.documents[i], similarities[i].item()) for i in top_indices]

# 使用示例
search_engine = SemanticSearch()
documents = [
    "人工智能是计算机科学的一个分支",
    "机器学习是实现人工智能的一种方法",
    "深度学习是机器学习的子领域",
    "自然语言处理让计算机理解人类语言",
    "计算机视觉让计算机理解图像"
]
search_engine.index_documents(documents)

results = search_engine.search("AI是什么", top_k=3)
for doc, score in results:
    print(f"相似度: {score:.4f} | {doc}")
