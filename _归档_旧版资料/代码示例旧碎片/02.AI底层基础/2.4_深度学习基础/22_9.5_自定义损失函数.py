# 示例1：带权重平衡的自定义损失（处理类别不平衡）
class WeightedCrossEntropyLoss(nn.Module):
    """带类别权重的交叉熵损失"""
    def __init__(self, weight=None):
        super().__init__()
        # weight: 各类别的权重 tensor
        self.weight = weight
    
    def forward(self, inputs, targets):
        return F.cross_entropy(inputs, targets, weight=self.weight)

# 示例2：Huber Loss（对异常值更鲁棒）
class HuberLoss(nn.Module):
    """Huber Loss：是MSE和MAE的折中
    
    当误差较小时使用MSE，误差较大时使用MAE
    参数:
        delta: 切换点，小于此值为MSE，大于此值为MAE
    """
    def __init__(self, delta=1.0):
        super().__init__()
        self.delta = delta
    
    def forward(self, pred, target):
        diff = torch.abs(pred - target)
        # 当 |error| <= delta 时使用MSE
        quadratic = torch.clamp(diff, max=self.delta)
        # 当 |error| > delta 时使用MAE
        linear = diff - quadratic
        # MSE: 0.5 * x^2, MAE: delta * (x - 0.5 * delta)
        loss = 0.5 * quadratic ** 2 + self.delta * linear
        return loss.mean()

# 测试Huber Loss对比MSE
pred = torch.tensor([10.0, 20.0, 30.0])
target = torch.tensor([12.0, 18.0, 35.0])

mse = nn.MSELoss()(pred, target)
huber = HuberLoss(delta=10.0)(pred, target)
print(f"MSE: {mse.item():.4f}, Huber: {huber.item():.4f}")

# 示例3：对比学习损失（SimCLR风格）
class ContrastiveLoss(nn.Module):
    """对比学习损失：拉近正样本，推远负样本
    
    参数:
        temperature: 温度参数，控制分布的锐度
    """
    def __init__(self, temperature=0.5):
        super().__init__()
        self.temperature = temperature
    
    def forward(self, z_i, z_j):
        """
        参数:
            z_i, z_j: 同一batch的两个视图的特征，形状为 (batch_size, dim)
        """
        batch_size = z_i.shape[0]
        
        # 归一化特征
        z_i = F.normalize(z_i, dim=1)
        z_j = F.normalize(z_j, dim=1)
        
        # 拼接所有样本 [2*batch, dim]
        z = torch.cat([z_i, z_j], dim=0)
        
        # 计算相似度矩阵
        sim_matrix = torch.matmul(z, z.T) / self.temperature
        
        # 创建标签：正样本对的位置
        # (i, i+batch) 和 (i+batch, i) 是正样本对
        labels = torch.arange(batch_size, device=z.device)
        labels = torch.cat([labels, labels], dim=0)
        
        # 只保留正样本对的损失
        loss = F.cross_entropy(sim_matrix, labels)
        return loss

# 示例4：自定义多任务损失
class MultiTaskLoss(nn.Module):
    """多任务学习的加权损失
    
    自动学习各任务损失的权重，使训练更稳定
    """
    def __init__(self, num_tasks, init_weights=None):
        super().__init__()
        # 使用对数方差参数化，使权重非负且可学习
        self.log_vars = nn.Parameter(torch.zeros(num_tasks))
        if init_weights:
            self.log_vars.data = torch.log(torch.tensor(init_weights))
    
    def forward(self, losses):
        """
        参数:
            losses: 各任务的损失列表
        """
        losses = torch.stack(losses)
        # 精度权重：exp(-log_var) 越大权重越高
        precision = torch.exp(-self.log_vars)
        # 加权求和 + log_var（平衡项）
        total_loss = torch.sum(precision * losses + self.log_vars)
        return total_loss

# 使用多任务损失
multi_task_loss = MultiTaskLoss(num_tasks=2, init_weights=[1.0, 0.5])
task_loss_1 = torch.tensor(0.5)
task_loss_2 = torch.tensor(1.2)
combined_loss = multi_task_loss([task_loss_1, task_loss_2])
print(f"多任务损失: {combined_loss.item():.4f}")
