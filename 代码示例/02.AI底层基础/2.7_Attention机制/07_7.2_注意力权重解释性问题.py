# 注意力权重显示模型"关注什么"，但不是决策依据

# 示例：模型可能均匀关注所有位置
# 但实际决策可能依赖于某个关键特征

# 解决方案：注意力可视化 + 其他解释方法
def analyze_attention(model, input_ids, tokenizer):
    """分析注意力权重"""
    with torch.no_grad():
        outputs = model(input_ids, output_attentions=True)
    
    attentions = outputs.attentions  # 各层的注意力
    
    # 分析最后一层
    last_layer_attn = attentions[-1]  # (batch, heads, seq, seq)
    
    # 找出高注意力位置
    avg_attn = last_layer_attn.mean(dim=1)  # 平均所有头
    top_positions = avg_attn.topk(5, dim=-1)
    
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0])
    print("Input tokens:", tokens)
    print("High attention positions:", top_positions.indices[0].tolist())
    
    return avg_attn, tokens
