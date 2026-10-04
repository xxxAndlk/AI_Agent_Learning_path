# Momentum原理解释
class MomentumOptimizer:
    """手动实现Momentum优化器"""
    def __init__(self, params, lr=0.01, momentum=0.9):
        self.params = list(params)
        self.lr = lr
        self.momentum = momentum
        # 保存每个参数的速度状态
        self.velocity = {id(p): torch.zeros_like(p) for p in self.params}
    
    def step(self):
        for p in self.params:
            if p.grad is None:
                continue
            
            param_id = id(p)
            # 更新速度：v = momentum * v + gradient
            self.velocity[param_id] = self.momentum * self.velocity[param_id] + p.grad.data
            
            # 更新参数：p = p - lr * v
            p.data = p.data - self.lr * self.velocity[param_id]
    
    def zero_grad(self):
        for p in self.params:
            p.grad = None

# 使用示例
model = nn.Linear(10, 1)
optimizer = MomentumOptimizer(model.parameters(), lr=0.01, momentum=0.9)
