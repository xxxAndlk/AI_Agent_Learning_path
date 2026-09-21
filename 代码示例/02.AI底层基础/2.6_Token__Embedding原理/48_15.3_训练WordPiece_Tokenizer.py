from tokenizers import Tokenizer, models, pre_tokenizers, trainers, decoders

def train_wordpiece_tokenizer():
    """训练WordPiece分词器"""
    
    # 1. 创建WordPiece模型
    tokenizer = Tokenizer(models.WordPiece())
    
    # 2. 设置预分词器
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.WhitespaceSplit(),  # 按空白分割
        pre_tokenizers.Punctuation(),      # 标点分割
    ])
    
    # 3. 配置训练器
    trainer = trainers.WordPieceTrainer(
        vocab_size=5000,
        min_frequency=2,
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
        show_progress=True,
    )
    
    # 4. 训练
    corpus = [
        "自然语言处理是人工智能的重要分支",
        "机器学习算法用于数据分析",
        "深度学习模型可以从数据中学习特征",
        "计算机视觉用于图像识别和分类",
    ]
    
    with open("corpus_wp.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(corpus))
    
    tokenizer.train(files=["corpus_wp.txt"], trainer=trainer)
    
    # 5. 解码器
    tokenizer.decoder = decoders.WordPiece()
    
    # 6. 测试
    text = "自然语言处理技术发展迅速"
    encoding = tokenizer.encode(text)
    
    print(f"原文: {text}")
    print(f"分词: {encoding.tokens}")
    print(f"IDs: {encoding.ids}")
    
    # 7. 保存
    tokenizer.save("custom_wordpiece_tokenizer.json")

train_wordpiece_tokenizer()
