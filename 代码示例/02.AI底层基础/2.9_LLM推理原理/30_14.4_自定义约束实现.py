"""
自定义约束解码实现
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Set

class ConstrainedDecoder:
    """自定义约束解码器"""
    
    def __init__(self, model_name: str):
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",
        )
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.eos_token_id = self.tokenizer.eos_token_id
    
    def generate_with_forbidden(
        self,
        prompt: str,
        forbidden_words: List[str],
        max_new_tokens: int = 100,
    ) -> str:
        """生成时禁止特定词汇"""
        
        # 将禁止词转为token IDs
        forbidden_ids = set()
        for word in forbidden_words:
            ids = self.tokenizer.encode(" " + word, add_special_tokens=False)
            forbidden_ids.update(ids)
        
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(
            self.model.device
        )
        generated = input_ids
        
        for _ in range(max_new_tokens):
            with torch.no_grad():
                outputs = self.model(generated)
                logits = outputs.logits[:, -1, :].squeeze(0)
                
                # 将禁止词的概率设为负无穷
                for token_id in forbidden_ids:
                    logits[token_id] = float("-inf")
                
                # 采样
                probs = torch.softmax(logits, dim=-1)
                next_token = torch.multinomial(probs, num_samples=1)
                
                if next_token.item() == self.eos_token_id:
                    break
            
            generated = torch.cat([generated, next_token], dim=1)
        
        return self.tokenizer.decode(generated[0], skip_special_tokens=True)
    
    def generate_with_pattern(
        self,
        prompt: str,
        allowed_first_chars: str,
        max_new_tokens: int = 100,
    ) -> str:
        """生成时限制首字符"""
        
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(
            self.model.device
        )
        generated = input_ids
        
        for step in range(max_new_tokens):
            with torch.no_grad():
                outputs = self.model(generated)
                logits = outputs.logits[:, -1, :].squeeze(0)
                
                # 第一步：限制首字符
                if step == 0 and allowed_first_chars:
                    for i in range(len(logits)):
                        token_text = self.tokenizer.decode(i)
                        if not token_text.startswith(allowed_first_chars):
                            logits[i] = float("-inf")
                
                next_token = torch.multinomial(torch.softmax(logits, dim=-1), 1)
                
                if next_token.item() == self.eos_token_id:
                    break
            
            generated = torch.cat([generated, next_token], dim=1)
        
        return self.tokenizer.decode(generated[0], skip_special_tokens=True)


# 使用示例
# decoder = ConstrainedDecoder("meta-llama/Llama-2-7b-chat-hf")
# result = decoder.generate_with_forbidden(
#     prompt="写一个故事：",
#     forbidden_words=["暴力", "血腥", "色情"],
# )
