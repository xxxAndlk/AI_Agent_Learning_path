# 权重衰减实现
optimizer = optim.AdamW(
    model.parameters(),
    lr=0.001,
    weight_decay=0.01  # 权重衰减系数
)

# 权重衰减的数学原理
# 带L2正则的损失: L' = L + λ/2 * ||w||²
# 参数更新: w = w - η * (∂L/∂w + λw) = w(1 - ηλ) - η*∂L/∂w
# 这就是"权重衰减"

# 不同优化器中weight_decay的行为
# AdamW: weight_decay在参数更新时应用
# Adam + L2: weight_decay在梯度上应用（两者数学上不完全等价）

# 手动实现权重衰减
class L2Regularization:
    """手动实现L2正则化"""
    def __init__(self, model, weight_decay):
        self.model = model
        self.weight_decay = weight_decay
    
    def penalty(self):
        """计算所有参数的L2范数平方和"""
        l2_penalty = 0
        for param in self.model.parameters():
            l2_penalty += torch.sum(param ** 2)
        return self.weight_decay * l2_penalty

# 使用
model = nn.Linear(10, 1)
reg = L2Regularization(model, weight_decay=0.01)

criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

x, y = torch.randn(32, 10), torch.randn(32, 1)

optimizer.zero_grad()
output = model(x)
loss = criterion(output, y)
# 手动添加L2正则项
loss_with_reg = loss + reg.penalty()
loss_with_reg.backward()
optimizer.step()
