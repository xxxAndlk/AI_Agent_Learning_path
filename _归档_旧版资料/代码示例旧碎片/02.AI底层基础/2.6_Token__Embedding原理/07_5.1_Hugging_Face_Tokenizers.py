from transformers import AutoTokenizer

# 在线加载（首次会下载）
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

# 离线加载（指定本地路径）
tokenizer = AutoTokenizer.from_pretrained("./local_tokenizer/")

# 快速分词器（Rust实现，速度提升10倍）
tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese", use_fast=True)

# 基本属性
print(f"词表大小: {tokenizer.vocab_size}")
print(f"特殊标记: {tokenizer.special_tokens_map}")
print(f"模型最大长度: {tokenizer.model_max_length}")
