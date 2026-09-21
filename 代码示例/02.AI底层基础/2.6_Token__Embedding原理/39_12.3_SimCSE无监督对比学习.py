from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F

class SimCSE:
    """SimCSE句子嵌入"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
    
    def mean_pooling(self, model_output, attention_mask):
        """平均池化"""
        token_embeddings = model_output.last_hidden_state
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.shape).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def encode(self, texts, batch_size=32):
        """编码句子"""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            
            encoded = self.tokenizer(
                batch,
                padding=True,
                truncation=True,
                max_length=128,
                return_tensors="pt"
            )
            
            with torch.no_grad():
                outputs = self.model(**encoded)
            
            embeddings = self.mean_pooling(outputs, encoded["attention_mask"])
            # 归一化
            embeddings = F.normalize(embeddings, p=2, dim=1)
            all_embeddings.append(embeddings)
        
        return torch.cat(all_embeddings, dim=0)
    
    def compute_contrastive_loss(self, embeddings, temperature=0.05):
        """对比学习损失
        
        对于每个句子，正样本是它的dropout版本
        """
        # 计算相似度矩阵
        similarity = torch.matmul(embeddings, embeddings.T) / temperature
        
        # 创建标签（对角线为正样本）
        batch_size = embeddings.shape[0]
        labels = torch.arange(batch_size, device=embeddings.device)
        
        # 计算损失
        loss = F.cross_entropy(similarity, labels)
        
        return loss

# 使用示例
def use_simcse():
    """使用SimCSE"""
    
    simcse = SimCSE("bert-base-chinese")
    
    sentences = [
        "人工智能正在改变世界",
        "AI技术正在改变世界",
        "今天天气真不错",
    ]
    
    embeddings = simcse.encode(sentences)
    
    print(f"句子嵌入形状: {embeddings.shape}")
    
    # 计算相似度
    similarity = torch.matmul(embeddings, embeddings.T)
    print("\n相似度矩阵:")
    print(similarity.numpy())

use_simcse()
