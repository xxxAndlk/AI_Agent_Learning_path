# 激活函数可视化对比
import torch
import torch.nn.functional as F

x = torch.linspace(-3, 3, 100)

# ReLU：简单高效
relu_out = F.relu(x)

# LeakyReLU：解决"神经元死亡"
leaky_out = F.leaky_relu(x, negative_slope=0.01)

# GELU：平滑过渡，Transformer首选
gelu_out = F.gelu(x)
