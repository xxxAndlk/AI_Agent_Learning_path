import torch
import torch.nn as nn
import torch.optim as optim

# 简单的线性模型
model = nn.Linear(10, 1)
criterion = nn.MSELoss()
optimizer = optim.SGD(model.parameters(), lr=0.01)

# 模拟训练
x = torch.randn(32, 10)
y = torch.randn(32, 1)

# 标准SGD步骤
optimizer.zero_grad()      # 1. 清空梯度
output = model(x)          # 2. 前向传播
loss = criterion(output, y)  # 3. 计算损失
loss.backward()            # 4. 反向传播计算梯度
optimizer.step()           # 5. 更新参数

# SGD with Momentum（添加动量加速收敛）
# 动量可以理解为：累积之前的梯度方向，帮助跳出局部最优
optimizer_momentum = optim.SGD(
    model.parameters(), 
    lr=0.01, 
    momentum=0.9,  # 动量系数，通常设为0.9
    nesterov=True  # 使用Nesterov动量，更精确的更新
)
