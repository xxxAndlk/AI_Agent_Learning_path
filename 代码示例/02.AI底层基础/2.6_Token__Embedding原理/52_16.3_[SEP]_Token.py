def sep_token_demo():
    """SEP token演示"""
    
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    
    # 单句（自动添加[SEP]）
    single = tokenizer.encode("深度学习")
    print(f"单句编码: {single}")
    print(f"Token: {tokenizer.convert_ids_to_tokens(single)}")
    
    # 句子对（手动指定）
    pair = tokenizer.encode("深度学习", "机器学习", add_special_tokens=False)
    print(f"\n句子对编码: {pair}")
    print(f"Token: {tokenizer.convert_ids_to_tokens(pair)}")
    
    # 使用pair参数（推荐）
    pair_encoded = tokenizer(
        "深度学习是AI的核心",
        "机器学习是实现AI的方法",
        return_tensors="pt"
    )
    
    print(f"\n使用pair参数:")
    print(f"Token IDs: {pair_encoded['input_ids']}")
    print(f"Token Type IDs: {pair_encoded['token_type_ids']}")
    # token_type_ids: 0表示第一个句子，1表示第二个句子

sep_token_demo()
