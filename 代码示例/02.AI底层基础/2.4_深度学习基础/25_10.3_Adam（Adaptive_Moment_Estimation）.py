# Adam优化器
optimizer = optim.Adam(
    model.parameters(), 
    lr=0.001,           # 学习率
    betas=(0.9, 0.999), # 一阶和二阶矩估计的衰减率
    eps=1e-8,           # 防止除零的微小常数
    weight_decay=0      # L2正则化强度
)

# Adam原理简化实现
class AdamOptimizer:
    """手动实现Adam优化器"""
    def __init__(self, params, lr=0.001, betas=(0.9, 0.999), eps=1e-8):
        self.params = list(params)
        self.lr = lr
        self.beta1, self.beta2 = betas
        self.eps = eps
        
        # 状态变量
        self.m = {id(p): torch.zeros_like(p) for p in self.params}  # 一阶矩
        self.v = {id(p): torch.zeros_like(p) for p in self.params}  # 二阶矩
        self.t = 0  # 时间步
    
    def step(self):
        self.t += 1
        for p in self.params:
            if p.grad is None:
                continue
            
            grad = p.grad.data
            param_id = id(p)
            
            # 更新一阶矩（动量）
            self.m[param_id] = self.beta1 * self.m[param_id] + (1 - self.beta1) * grad
            # 更新二阶矩（方差）
            self.v[param_id] = self.beta2 * self.v[param_id] + (1 - self.beta2) * (grad ** 2)
            
            # 偏差校正
            m_hat = self.m[param_id] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_id] / (1 - self.beta2 ** self.t)
            
            # 更新参数
            p.data = p.data - self.lr * m_hat / (torch.sqrt(v_hat) + self.eps)
    
    def zero_grad(self):
        for p in self.params:
            p.grad = None
