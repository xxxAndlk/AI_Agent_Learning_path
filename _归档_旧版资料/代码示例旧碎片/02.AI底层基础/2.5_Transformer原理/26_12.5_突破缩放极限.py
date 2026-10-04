# 1. 稀疏专家模型 (MoE)
class MoELayer(nn.Module):
    """Mixture of Experts - 计算量不变，增加参数量"""
    
    def __init__(self, embed_size, num_experts=8, top_k=2):
        super().__init__()
        self.experts = nn.ModuleList([
            nn.Sequential(
                nn.Linear(embed_size, 4 * embed_size),
                nn.GELU(),
                nn.Linear(4 * embed_size, embed_size)
            ) for _ in range(num_experts)
        ])
        self.gate = nn.Linear(embed_size, num_experts)
        self.top_k = top_k
    
    def forward(self, x):
        # 门控选择top-k专家
        gate_logits = self.gate(x)
        top_k_logits, top_k_indices = torch.topk(gate_logits, self.top_k, dim=-1)
        
        # 计算加权输出
        output = torch.zeros_like(x)
        for i in range(self.top_k):
            expert_idx = top_k_indices[:, :, i]
            expert_weight = torch.softmax(top_k_logits, dim=-1)[:, :, i:i+1]
            
            # 选择对应专家的输出
            expert_output = torch.stack([
                self.experts[j](x) for j in range(len(self.experts))
            ], dim=2)
            
            # 使用gather选择当前token的专家
            output += expert_output.gather(2, expert_idx.unsqueeze(-1).expand(-1, -1, -1, expert_output.size(-1))).squeeze(2) * expert_weight
        
        return output

# 2. 持续预训练 (Continual Pre-training)
# 3. 课程学习 (Curriculum Learning)
# 4. 知识蒸馏 (Knowledge Distillation)
