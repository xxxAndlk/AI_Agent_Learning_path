def mask_token_demo():
    """MASK token演示"""
    
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    model = AutoModel.from_pretrained("bert-base-chinese")
    
    # MLM预训练数据示例
    text = "深度学习是[MASK]的核心技术"
    
    inputs = tokenizer(text, return_tensors="pt")
    
    # 找到[MASK]位置
    mask_token_id = tokenizer.mask_token_id
    mask_positions = (inputs["input_ids"] == mask_token_id).nonzero()
    print(f"[MASK]位置: {mask_positions}")
    
    # 预测[MASK]的内容
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 获取[MASK]位置的logits
    mask_logits = outputs.last_hidden_state[0, mask_positions[0, 1], :]
    
    # Top-5预测
    top_k = 5
    top_indices = torch.topk(mask_logits, top_k).indices
    top_tokens = tokenizer.convert_ids_to_tokens(top_indices)
    top_probs = torch.softmax(mask_logits, dim=-1)[top_indices]
    
    print(f"\n[MASK]预测结果:")
    for token, prob in zip(top_tokens, top_probs):
        print(f"  {token}: {prob:.4f}")

mask_token_demo()
