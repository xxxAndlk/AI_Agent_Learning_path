# 1. 梯度裁剪
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

# 2. 学习率预热
from torch.optim.lr_scheduler import LambdaLR
def warmup_lambda(epoch):
    return min(1.0, (epoch + 1) / 10)  # 前10个epoch逐渐增加学习率
scheduler = LambdaLR(optimizer, lr_lambda=warmup_lambda)

# 3. 混合精度训练（减少数值不稳定）
from torch.amp import autocast, GradScaler  # PyTorch 2.x起torch.cuda.amp已弃用，统一从torch.amp导入
scaler = GradScaler()

with autocast("cuda"):
    output = model(data)
    loss = criterion(output, target)
scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()

# 4. 权重初始化
def init_weights(m):
    if isinstance(m, nn.Linear):
        nn.init.xavier_uniform_(m.weight)
        nn.init.zeros_(m.bias)
model.apply(init_weights)
