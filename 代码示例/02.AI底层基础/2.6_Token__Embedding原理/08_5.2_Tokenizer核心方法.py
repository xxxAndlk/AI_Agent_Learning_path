from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")

text = "深度学习改变世界"

# ========== 方法1: tokenize ==========
# 功能: 纯分词，返回token字符串列表
tokens = tokenizer.tokenize(text)
# 输出: ['深', '度', '学', '习', '改', '变', '世', '界']

# ========== 方法2: encode ==========
# 功能: 分词 + 编码，返回token ID列表
input_ids = tokenizer.encode(text, add_special_tokens=True)
# 输出: [101, 3821, 2450, 2110, 739, 2842, 1344, 686, 4510, 102]
#       [CLS]  深    度    学    习   改   变   世   界   [SEP]

# ========== 方法3: decode ==========
# 功能: ID → 文本
decoded = tokenizer.decode(input_ids)
# 输出: "[CLS] 深度学习改变世界 [SEP]"

# ========== 方法4: __call__ (推荐) ==========
# 功能: 一站式编码，返回字典
encoding = tokenizer(
    text,
    padding="max_length",    # 填充到最大长度
    truncation=True,         # 超长截断
    max_length=20,           # 指定长度
    return_tensors="pt"       # 返回PyTorch张量
)
# 返回: {
#   "input_ids": tensor([[101, ..., 102, 0, 0, ...]]),
#   "attention_mask": tensor([[1, 1, ..., 1, 0, 0, ...]]),
#   "token_type_ids": tensor([[0, 0, ..., 0, 0, 0, ...]])
# }
