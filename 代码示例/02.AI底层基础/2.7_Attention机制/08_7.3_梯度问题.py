# 问题：训练初期注意力权重可能过于尖锐或过于平坦

# 解决方案1：注意力温度调整
class TemperatureScaledAttention(nn.Module):
    def __init__(self, d_k, initial_temperature=1.0):
        super().__init__()
        self.temperature = nn.Parameter(torch.tensor(initial_temperature))
        self.scale = math.sqrt(d_k)
    
    def forward(self, Q, K, V, mask=None):
        scores = torch.matmul(Q, K.transpose(-2, -1)) / (self.scale * self.temperature)
        # ... 后续处理

# 解决方案2：梯度裁剪
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# 解决方案3：注意力Dropout
attention = F.dropout(attention, p=0.1, training=self.training)
