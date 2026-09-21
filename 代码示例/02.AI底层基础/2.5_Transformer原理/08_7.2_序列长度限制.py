# 1. 分段处理
def process_long_text(text, max_length=512, stride=256):
    tokens = tokenize(text)
    chunks = []
    for i in range(0, len(tokens), stride):
        chunk = tokens[i:i+max_length]
        chunks.append(chunk)
    return chunks

# 2. 使用长序列模型
# - Longformer: 稀疏注意力，支持4096+ tokens
# - Reformer: 局部敏感哈希，O(n log n)
# - Transformer-XL: 段级递归，保持上下文
