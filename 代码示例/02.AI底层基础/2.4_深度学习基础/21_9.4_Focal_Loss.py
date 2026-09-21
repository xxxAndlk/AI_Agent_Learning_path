import torch
import torch.nn as nn
import torch.nn.functional as F

class FocalLoss(nn.Module):
    """Focal Loss实现
    
    参数:
        alpha: 类别权重，可为标量或列表
        gamma: 聚焦参数，默认值为2
        reduction: 损失聚合方式，可选'none', 'mean', 'sum'
    """
    def __init__(self, alpha=1.0, gamma=2.0, reduction='mean'):
        super().__init__()
        self.alpha = alpha  # 正负样本平衡权重
        self.gamma = gamma  # 聚焦参数
        self.reduction = reduction
    
    def forward(self, inputs, targets):
        """
        参数:
            inputs: 模型的原始输出 (batch_size, num_classes)
            targets: 真实标签 (batch_size,)
        """
        # 计算交叉熵
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        
        # 获取真实类别的概率
        pt = torch.exp(-ce_loss)
        
        # 计算focal term
        focal_term = (1 - pt) ** self.gamma
        
        # 计算最终损失
        loss = self.alpha * focal_term * ce_loss
        
        if self.reduction == 'mean':
            return loss.mean()
        elif self.reduction == 'sum':
            return loss.sum()
        else:
            return loss

# 使用示例
criterion = FocalLoss(alpha=1.0, gamma=2.0)

# 模拟多分类输出
logits = torch.randn(8, 10)
targets = torch.tensor([3, 7, 1, 5, 2, 8, 0, 4])

loss = criterion(logits, targets)
print(f"Focal Loss: {loss.item():.4f}")

# 带类别权重的Focal Loss（处理类别不平衡）
class FocalLossWithAlpha(nn.Module):
    """带类别权重的Focal Loss"""
    def __init__(self, alpha, gamma=2.0):
        super().__init__()
        self.alpha = alpha  # 列表，长度为类别数
        self.gamma = gamma
    
    def forward(self, inputs, targets):
        ce_loss = F.cross_entropy(inputs, targets, reduction='none')
        pt = torch.exp(-ce_loss)
        
        # 根据真实类别获取对应的alpha权重
        if isinstance(self.alpha, (list, torch.Tensor)):
            alpha_t = torch.tensor(self.alpha, device=inputs.device)[targets]
        else:
            alpha_t = self.alpha
        
        focal_term = (1 - pt) ** self.gamma
        loss = alpha_t * focal_term * ce_loss
        return loss.mean()

# 类别不平衡示例：类别0和1样本多，类别8和9样本少
# 给少样本类别更高的权重
alpha_weights = [1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 2.0, 2.0]
criterion_imbalanced = FocalLossWithAlpha(alpha_weights)
loss_imbalanced = criterion_imbalanced(logits, targets)
print(f"Focal Loss (带类别权重): {loss_imbalanced.item():.4f}")
