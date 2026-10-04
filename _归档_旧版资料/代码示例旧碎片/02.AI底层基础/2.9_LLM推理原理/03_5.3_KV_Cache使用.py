def generate_with_kv_cache(model, tokenizer, prompt, max_new_tokens=100):
    """使用KV Cache的生成"""
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
    # 初始化KV Cache
    past_key_values = None
    
    for _ in range(max_new_tokens):
        with torch.no_grad():
            # 只传入最新的token和缓存的KV
            outputs = model(
                input_ids[:, -1:] if past_key_values else input_ids,
                past_key_values=past_key_values,
                use_cache=True
            )
        
        logits = outputs.logits[:, -1, :]
        past_key_values = outputs.past_key_values  # 更新缓存
        
        # 采样
        next_token = torch.argmax(logits, dim=-1, keepdim=True)
        input_ids = torch.cat([input_ids, next_token], dim=-1)
        
        if next_token.item() == tokenizer.eos_token_id:
            break
    
    return tokenizer.decode(input_ids[0], skip_special_tokens=True)
