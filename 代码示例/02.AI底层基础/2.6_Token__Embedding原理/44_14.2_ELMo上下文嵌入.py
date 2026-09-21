from transformers import AutoModel, AutoTokenizer
import torch

# 使用BERT实现类似ELMo的多层嵌入
def get_contextual_embeddings():
    """获取BERT的多层上下文嵌入"""
    
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    model = AutoModel.from_pretrained("bert-base-chinese")
    model.eval()
    
    # 同一词在不同上下文中的句子
    sentences = [
        "我去银行存钱",  # 金融机构
        "银行里的水流向河里",  # 河流
    ]
    
    print("=" * 60)
    print("上下文嵌入演示：'银行'在不同句子中的向量")
    print("=" * 60)
    
    embeddings_per_layer = []
    
    for sentence in sentences:
        inputs = tokenizer(sentence, return_tensors="pt", padding=True)
        
        with torch.no_grad():
            # 获取所有层的输出
            outputs = model(**inputs, output_hidden_states=True)
        
        # hidden_states: tuple of (num_layers+1) × (batch, seq_len, hidden_dim)
        hidden_states = outputs.hidden_states
        
        # 找到"银行"的位置
        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        bank_idx = tokens.index("银")
        
        print(f"\n句子: {sentence}")
        print(f"分词: {tokens}")
        print(f"'银'的位置: {bank_idx}")
        
        # 提取各层的"银"向量
        layer_embeddings = []
        for i, hidden in enumerate(hidden_states):
            # 第i层的[CLS]位置之后的第bank_idx个token
            emb = hidden[0, bank_idx + 1, :].numpy()  # +1跳过[CLS]
            layer_embeddings.append(emb)
        
        embeddings_per_layer.append(layer_embeddings)
        
        # 显示各层向量的统计信息
        print(f"各层向量范数: ", end="")
        for i, emb in enumerate(layer_embeddings):
            norm = np.linalg.norm(emb)
            print(f"L{i}:{norm:.2f} ", end="")
        print()
    
    # 比较两个上下文中"银行"的差异
    import numpy as np
    
    diff = embeddings_per_layer[0][-1] - embeddings_per_layer[1][-1]
    print(f"\n两个上下文在最后一层的向量差异: {np.linalg.norm(diff):.4f}")

get_contextual_embeddings()
