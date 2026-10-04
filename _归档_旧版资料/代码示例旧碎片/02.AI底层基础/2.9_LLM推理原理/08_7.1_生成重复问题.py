# 问题：输出 "今天天气很好，天气很好，天气很好..."

# 解决方案1：重复惩罚
def apply_repetition_penalty(logits, input_ids, penalty=1.2):
    """重复惩罚：降低已出现token的概率"""
    for token_id in input_ids[0]:
        logits[0, token_id] /= penalty
    return logits

# 解决方案2：调整温度
temperature = 0.7  # 适当提高温度增加多样性

# 解决方案3：使用更好的采样策略
# Top-P + Top-K 组合
