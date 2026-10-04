from transformers import AutoModel, AutoTokenizer
import torch

def cls_token_demo():
    """CLS token演示"""
    
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    model = AutoModel.from_pretrained("bert-base-chinese")
    model.eval()
    
    text = "深度学习非常有趣"
    
    # 编码
    inputs = tokenizer(text, return_tensors="pt")
    
    # 查看[CLS]位置
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
    print(f"Tokens: {tokens}")
    print(f"[CLS]位置: {tokens.index('[CLS]')}")
    
    # 提取[CLS]向量
    with torch.no_grad():
        outputs = model(**inputs)
    
    cls_embedding = outputs.last_hidden_state[:, 0, :]
    print(f"[CLS]向量形状: {cls_embedding.shape}")
    
    # [CLS]用于分类
    # 例如文本分类
    classifier = torch.nn.Linear(768, 2)
    logits = classifier(cls_embedding)
    print(f"分类logits: {logits}")

cls_token_demo()
