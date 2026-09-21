# 1. 填充掩码 (Padding Mask)
# 处理变长序列，忽略填充位置
def create_padding_mask(seq, pad_token=0):
    """
    seq: (batch_size, seq_len)
    返回: (batch_size, 1, 1, seq_len)
    """
    mask = (seq != pad_token).unsqueeze(1).unsqueeze(2)
    return mask  # True位置保留，False位置被mask

# 2. 前瞻掩码 (Look-ahead Mask / Causal Mask)
# 解码器中使用，防止看到未来信息
def create_causal_mask(seq_len):
    """
    创建上三角为0的下三角矩阵
    位置i只能看到位置0到i的信息
    """
    mask = torch.tril(torch.ones(seq_len, seq_len))
    return mask  # 下三角为1，上三角为0

# 示例: seq_len=4时的causal mask
# [[1, 0, 0, 0],
#  [1, 1, 0, 0],
#  [1, 1, 1, 0],
#  [1, 1, 1, 1]]
# 位置0只能看位置0
# 位置1可以看位置0,1
# 位置2可以看位置0,1,2
# 位置3可以看位置0,1,2,3
