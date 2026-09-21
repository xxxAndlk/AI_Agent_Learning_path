def create_padding_mask(seq, pad_token=0):
    """创建填充掩码
    
    Args:
        seq: (batch_size, seq_len) 输入序列
        pad_token: padding token的ID
    
    Returns:
        mask: (batch_size, 1, 1, seq_len)
    """
    mask = (seq != pad_token).unsqueeze(1).unsqueeze(2)
    return mask

def create_causal_mask(seq_len):
    """创建因果掩码（下三角矩阵）
    
    Args:
        seq_len: 序列长度
    
    Returns:
        mask: (1, 1, seq_len, seq_len)
    """
    mask = torch.tril(torch.ones(seq_len, seq_len))
    return mask.unsqueeze(0).unsqueeze(0)

def create_combined_mask(tgt, pad_token=0):
    """组合填充掩码和因果掩码"""
    tgt_mask = create_causal_mask(tgt.shape[1])
    padding_mask = create_padding_mask(tgt, pad_token)
    return tgt_mask & padding_mask
