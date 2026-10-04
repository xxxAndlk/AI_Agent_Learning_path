def pad_token_demo():
    """PAD token演示"""
    
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    
    # 批量编码
    texts = [
        "深度学习",                  # 短
        "深度学习是人工智能的核心",  # 长
    ]
    
    encoded = tokenizer(
        texts,
        padding="max_length",       # 填充到最大长度
        max_length=10,
        return_tensors="pt"
    )
    
    print("PAD处理演示:")
    print(f"input_ids:\n{encoded['input_ids']}")
    print(f"\nattention_mask:\n{encoded['attention_mask']}")
    # attention_mask: 1=有效token, 0=padding
    
    # 检查PAD ID
    print(f"\nPAD token ID: {tokenizer.pad_token_id}")
    print(f"PAD token: {tokenizer.pad_token}")

pad_token_demo()
