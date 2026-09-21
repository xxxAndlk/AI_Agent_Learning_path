# 手动实现LoRA层
import torch
import torch.nn as nn

class LoRALayer(nn.Module):
    def __init__(self, in_features, out_features, r=16, alpha=32):
        super().__init__()
        self.r = r
        self.alpha = alpha
        self.scaling = alpha / r
        
        # 原始线性层（冻结）
        self.original = nn.Linear(in_features, out_features)
        for param in self.original.parameters():
            param.requires_grad = False
        
        # LoRA低秩矩阵
        self.lora_A = nn.Parameter(torch.zeros(r, in_features))
        self.lora_B = nn.Parameter(torch.zeros(out_features, r))
        
        # 初始化
        nn.init.kaiming_uniform_(self.lora_A, a=5**0.5)
        nn.init.zeros_(self.lora_B)  # B初始化为0
    
    def forward(self, x):
        # 原始输出
        result = self.original(x)
        # LoRA增量
        lora_output = (x @ self.lora_A.T) @ self.lora_B.T * self.scaling
        return result + lora_output
