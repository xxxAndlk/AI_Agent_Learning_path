# 梯度裁剪示例
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# Xavier初始化（适用于Sigmoid/Tanh）
nn.init.xavier_uniform_(layer.weight)

# Kaiming初始化（适用于ReLU）
nn.init.kaiming_normal_(layer.weight, mode='fan_out', nonlinearity='relu')
