import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

def text_similarity_demo():
    """计算文本相似度完整示例"""
    
    # 加载中文模型
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    model = AutoModel.from_pretrained("bert-base-chinese")
    model.eval()  # 评估模式
    
    # 待比较的文本对
    texts = [
        "人工智能正在改变世界",
        "AI技术正在改变世界",      # 语义相近
        "今天天气真不错",           # 语义无关
    ]
    
    # 编码文本
    encoded = tokenizer(
        texts,
        padding=True,
        truncation=True,
        max_length=32,
        return_tensors="pt"
    )
    
    # 获取BERT嵌入
    with torch.no_grad():
        outputs = model(**encoded)
        # 使用[CLS]位置的向量作为句子表示
        # last_hidden_state: (batch, seq_len, hidden_dim)
        cls_embeddings = outputs.last_hidden_state[:, 0, :]  # (batch, hidden_dim)
    
    # 计算相似度矩阵
    similarity_matrix = F.cosine_similarity(
        cls_embeddings.unsqueeze(1),  # (3, 1, 768)
        cls_embeddings.unsqueeze(0),  # (1, 3, 768)
        dim=2
    )
    
    print("相似度矩阵:")
    print(similarity_matrix)
    # 预期结果：
    # - texts[0]与texts[1]相似度较高（都讲AI改变世界）
    # - texts[0]与texts[2]相似度较低（主题不同）

if __name__ == "__main__":
    text_similarity_demo()
