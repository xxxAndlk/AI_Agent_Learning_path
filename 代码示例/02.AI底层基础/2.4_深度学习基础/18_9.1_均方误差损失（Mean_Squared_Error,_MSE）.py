import torch
import torch.nn as nn

# 方法1：使用PyTorch内置函数
criterion = nn.MSELoss()

# 模拟预测值和真实值
predictions = torch.tensor([2.5, 3.8, 5.1, 4.6], requires_grad=True)
targets = torch.tensor([2.7, 3.6, 5.5, 4.3])

loss = criterion(predictions, targets)
print(f"MSE Loss: {loss.item():.4f}")  # 输出约 0.085

# 方法2：手动实现
def mse_loss(pred, target):
    """手动实现MSE损失"""
    return torch.mean((pred - target) ** 2)

manual_loss = mse_loss(predictions, targets)
print(f"手动MSE Loss: {manual_loss.item():.4f}")
