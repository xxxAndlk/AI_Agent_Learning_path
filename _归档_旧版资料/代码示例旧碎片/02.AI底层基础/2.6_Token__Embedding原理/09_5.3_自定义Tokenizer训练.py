from tokenizers import Tokenizer, models, pre_tokenizers, trainers

# 1. 创建BPE tokenizer
tokenizer = Tokenizer(models.BPE())

# 2. 设置预分词器（按空格和标点分割）
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

# 3. 配置训练器
trainer = trainers.BpeTrainer(
    vocab_size=10000,        # 目标词表大小
    special_tokens=["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"]
)

# 4. 在语料上训练
tokenizer.train(
    files=["corpus.txt"],    # 训练语料
    trainer=trainer
)

# 5. 保存
tokenizer.save("custom_tokenizer.json")
