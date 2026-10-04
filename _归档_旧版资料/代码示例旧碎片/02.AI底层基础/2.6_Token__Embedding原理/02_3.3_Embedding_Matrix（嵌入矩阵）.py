# BERT-base配置
vocab_size = 30522
embed_dim = 768
params = vocab_size * embed_dim  # 23,440,896 参数
memory_mb = params * 4 / (1024 * 1024)  # 约89MB (float32)
