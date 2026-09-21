import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

def basic_generate(model, tokenizer, prompt, max_new_tokens=100):
    """基础自回归生成"""
    input_ids = tokenizer.encode(prompt, return_tensors="pt")
    
    for _ in range(max_new_tokens):
        # 前向传播
        with torch.no_grad():
            outputs = model(input_ids)
            logits = outputs.logits[:, -1, :]  # 取最后一个位置
        
        # 贪婪采样
        next_token = torch.argmax(logits, dim=-1, keepdim=True)
        
        # 追加到序列
        input_ids = torch.cat([input_ids, next_token], dim=-1)
        
        # 检查结束符
        if next_token.item() == tokenizer.eos_token_id:
            break
    
    return tokenizer.decode(input_ids[0], skip_special_tokens=True)
