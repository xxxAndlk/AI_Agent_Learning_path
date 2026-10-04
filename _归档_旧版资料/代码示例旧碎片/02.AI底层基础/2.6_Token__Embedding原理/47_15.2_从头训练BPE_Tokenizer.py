from tokenizers import Tokenizer, models, pre_tokenizers, trainers, decoders

def train_bpe_tokenizer():
    """训练BPE分词器"""
    
    # 1. 创建空的BPE模型
    tokenizer = Tokenizer(models.BPE())
    
    # 2. 设置预分词器（按空白字符和标点分割）
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.Whitespace(),           # 空白字符分割
        pre_tokenizers.Punctuation(),          # 标点分割
    ])
    
    # 3. 配置训练器
    trainer = trainers.BpeTrainer(
        vocab_size=10000,              # 目标词表大小
        min_frequency=2,               # 最小频率阈值
        special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"],
        show_progress=True,
        # 持续训练直到达到目标词表大小
        continuing_subword_prefix="##",  # 子词前缀（可选）
    )
    
    # 4. 准备训练语料
    corpus = [
        "深度学习是人工智能的核心技术",
        "自然语言处理用于文本分析",
        "机器学习包括监督学习和无监督学习",
        "深度学习模型包括CNN和RNN",
        "Transformer在NLP领域取得了巨大成功",
        "注意力机制是Transformer的核心",
    ]
    
    # 写入临时文件
    with open("corpus.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(corpus))
    
    # 5. 训练
    tokenizer.train(files=["corpus.txt"], trainer=trainer)
    
    # 6. 添加解码器
    tokenizer.decoder = decoders.BPEDecoder(suffix="##")
    
    # 7. 测试
    text = "深度学习是非常有趣的技术"
    encoding = tokenizer.encode(text)
    
    print(f"原文: {text}")
    print(f"分词: {encoding.tokens}")
    print(f"IDs: {encoding.ids}")
    
    # 解码
    decoded = tokenizer.decode(encoding.ids)
    print(f"解码: {decoded}")
    
    # 8. 保存
    tokenizer.save("custom_bpe_tokenizer.json")
    print("\nTokenizer已保存!")

train_bpe_tokenizer()
