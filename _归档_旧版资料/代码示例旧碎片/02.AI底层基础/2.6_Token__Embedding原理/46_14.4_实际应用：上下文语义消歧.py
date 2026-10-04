def contextual_word_disambiguation():
    """上下文词义消歧示例"""
    
    extractor = BertEmbeddingExtractor()
    
    # 同一词在不同上下文
    contexts = [
        "我把钱存到银行",      # 金融机构
        "河水从银行流过",     # 河岸
        "银行利率最近上涨",   # 金融机构
    ]
    
    # 提取"银行"的上下文嵌入
    print("'银行'在不同上下文中的嵌入相似度:")
    print("-" * 50)
    
    embeddings = []
    for ctx in contexts:
        emb = extractor.extract_embeddings(ctx, pooling="mean")
        embeddings.append(emb[0].numpy())
    
    import numpy as np
    
    # 计算相似度
    for i in range(len(contexts)):
        for j in range(i + 1, len(contexts)):
            sim = np.dot(embeddings[i], embeddings[j]) / (
                np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j])
            )
            print(f"'{contexts[i]}' vs '{contexts[j]}'")
            print(f"  相似度: {sim:.4f}")

contextual_word_disambiguation()
