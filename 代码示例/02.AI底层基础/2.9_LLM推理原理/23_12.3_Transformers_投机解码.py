"""
使用Transformers实现自定义投机解码
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from typing import List, Optional

class SpeculativeDecoder:
    """投机解码器实现"""
    
    def __init__(
        self,
        main_model_name: str,
        draft_model_name: str,
        num_speculative_tokens: int = 5,
    ):
        """初始化主模型和草稿模型"""
        self.num_spec = num_speculative_tokens
        
        print(f"加载主模型: {main_model_name}")
        self.main_model = AutoModelForCausalLM.from_pretrained(
            main_model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        
        print(f"加载草稿模型: {draft_model_name}")
        self.draft_model = AutoModelForCausalLM.from_pretrained(
            draft_model_name,
            torch_dtype=torch.float16,
            device_map="auto",
            trust_remote_code=True,
        )
        
        self.tokenizer = AutoTokenizer.from_pretrained(main_model_name)
        
        # 设置pad token
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
    
    def generate_speculative(
        self,
        prompt: str,
        max_new_tokens: int = 100,
    ) -> str:
        """投机解码生成"""
        input_ids = self.tokenizer.encode(prompt, return_tensors="pt").to(
            self.main_model.device
        )
        
        generated = input_ids.clone()
        
        for _ in range(max_new_tokens):
            # Step 1: 草稿模型生成候选
            draft_ids = generated
            
            draft_outputs = []
            with torch.no_grad():
                for _ in range(self.num_spec):
                    outputs = self.draft_model(draft_ids)
                    next_token = torch.argmax(outputs.logits[:, -1, :], dim=-1)
                    draft_outputs.append(next_token.item())
                    draft_ids = torch.cat([draft_ids, next_token.unsqueeze(1)], dim=1)
                    
                    if next_token.item() == self.tokenizer.eos_token_id:
                        break
            
            if not draft_outputs:
                break
            
            # Step 2: 主模型验证（批量验证更高效）
            combined_ids = torch.cat([
                generated,
                torch.tensor([draft_outputs], device=generated.device)
            ], dim=1)
            
            with torch.no_grad():
                outputs = self.main_model(combined_ids)
            
            # Step 3: 验证每个草稿token
            accepted_tokens = []
            main_tokens = torch.argmax(outputs.logits, dim=-1)[0]
            
            for i, draft_token in enumerate(draft_outputs):
                if i >= len(main_tokens) - 1:
                    break
                    
                main_token = main_tokens[i + len(generated[0]) - 1].item()
                
                if draft_token == main_token:
                    accepted_tokens.append(draft_token)
                else:
                    # 第一个不匹配后停止接受
                    accepted_tokens.append(main_token)
                    break
            
            # 添加接受的tokens
            new_tokens = torch.tensor([accepted_tokens], device=generated.device)
            generated = torch.cat([generated, new_tokens], dim=1)
            
            # 检查是否遇到结束符
            if accepted_tokens[-1] == self.tokenizer.eos_token_id:
                break
        
        return self.tokenizer.decode(generated[0], skip_special_tokens=True)


# 使用示例
# decoder = SpeculativeDecoder(
#     main_model_name="meta-llama/Llama-2-70b-hf",
#     draft_model_name="meta-llama/Llama-2-7b-hf",
#     num_speculative_tokens=5,
# )
# result = decoder.generate_speculative("写一个关于Python的教程：")
