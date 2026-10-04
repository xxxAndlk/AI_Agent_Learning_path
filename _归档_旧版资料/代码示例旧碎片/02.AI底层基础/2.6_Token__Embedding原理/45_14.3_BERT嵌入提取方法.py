from transformers import AutoModel, AutoTokenizer
import torch
import torch.nn.functional as F

class BertEmbeddingExtractor:
    """BERT嵌入提取器"""
    
    def __init__(self, model_name="bert-base-chinese"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        
        # 隐藏层大小
        self.hidden_size = self.model.config.hidden_size
    
    def extract_embeddings(self, text, layer=None, pooling="cls"):
        """提取嵌入
        
        参数:
            text: 输入文本
            layer: 指定层（None表示最后一层）
            pooling: 池化方式 ("cls", "mean", "max")
        """
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        # 获取隐藏状态
        hidden_states = outputs.hidden_states
        
        if layer is None:
            # 使用最后一层
            hidden_state = hidden_states[-1]
        else:
            hidden_state = hidden_states[layer]
        
        # 池化
        if pooling == "cls":
            # [CLS]向量
            embedding = hidden_state[:, 0, :]
        elif pooling == "mean":
            # 平均池化
            attention_mask = inputs["attention_mask"]
            mask_expanded = attention_mask.unsqueeze(-1).expand(hidden_state.size()).float()
            sum_embeddings = torch.sum(hidden_state * mask_expanded, 1)
            sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
            embedding = sum_embeddings / sum_mask
        elif pooling == "max":
            # 最大池化
            attention_mask = inputs["attention_mask"]
            hidden_state[attention_mask == 0] = -1e9
            embedding = torch.max(hidden_state, dim=1)[0]
        
        return embedding
    
    def extract_all_layers(self, text, pooling="mean"):
        """提取所有层的嵌入并拼接"""
        
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            padding=True,
            truncation=True
        )
        
        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
        
        hidden_states = outputs.hidden_states[1:]  # 去掉embedding层
        
        # 各层池化后拼接
        all_embeddings = []
        attention_mask = inputs["attention_mask"]
        
        for hidden in hidden_states:
            # 平均池化
            mask_expanded = attention_mask.unsqueeze(-1).expand(hidden.size()).float()
            sum_embeddings = torch.sum(hidden * mask_expanded, 1)
            sum_mask = torch.clamp(mask_expanded.sum(1), min=1e-9)
            embedding = sum_embeddings / sum_mask
            all_embeddings.append(embedding)
        
        # 拼接所有层
        concatenated = torch.cat(all_embeddings, dim=-1)
        
        return concatenated

# 使用示例
def demo_embedding_extraction():
    """嵌入提取演示"""
    
    extractor = BertEmbeddingExtractor()
    
    text = "深度学习是非常有趣的技术"
    
    # 提取最后一层[CLS]向量
    cls_emb = extractor.extract_embeddings(text, layer=None, pooling="cls")
    print(f"[CLS]向量形状: {cls_emb.shape}")
    
    # 提取最后一层平均向量
    mean_emb = extractor.extract_embeddings(text, pooling="mean")
    print(f"平均向量形状: {mean_emb.shape}")
    
    # 提取所有层
    all_layers_emb = extractor.extract_all_layers(text)
    print(f"所有层拼接形状: {all_layers_emb.shape}")
    # BERT-base: 12层 × 768维 = 9216维

demo_embedding_extraction()
