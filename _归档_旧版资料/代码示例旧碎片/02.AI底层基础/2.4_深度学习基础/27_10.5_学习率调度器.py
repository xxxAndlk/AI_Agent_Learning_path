# 常用学习率调度器
scheduler_config = {
    # 1. 固定学习率（无调度）
    'constant': optim.lr_scheduler.LambdaLR(
        optimizer, lr_lambda=lambda epoch: 1.0
    ),
    
    # 2. 指数衰减：每个epoch学习率乘以gamma
    'exponential': optim.lr_scheduler.ExponentialLR(
        optimizer, gamma=0.95
    ),
    
    # 3. 阶梯衰减：每N个epoch后学习率乘以gamma
    'step': optim.lr_scheduler.StepLR(
        optimizer, step_size=10, gamma=0.1
    ),
    
    # 4. 余弦退火：从初始学习率逐渐降到最小值再上升（周期型）
    'cosine': optim.lr_scheduler.CosineAnnealingLR(
        optimizer, T_max=50, eta_min=1e-6
    ),
    
    # 5. 余弦退火warm restarts：在余弦基础上周期性重置学习率
    'cosine_warmup': optim.lr_scheduler.CosineAnnealingWarmRestarts(
        optimizer, T_0=10, T_mult=2
    ),
    
    # 6. 学习率预热 + 余弦衰减（Transformer推荐）
    'warmup_cosine': None,  # 需要自定义
    
    # 7. ReduceLROnPlateau：当指标停止改善时降低学习率
    'plateau': optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.1, patience=5
    ),
}

# 自定义学习率预热 + 余弦衰减调度器
class WarmupCosineScheduler:
    """学习率预热 + 余弦退火调度器
    
    参数:
        optimizer: 优化器
        warmup_epochs: 预热epoch数
        max_epochs: 总训练epoch数
        min_lr: 最小学习率
        base_lr: 基础学习率
    """
    def __init__(self, optimizer, warmup_epochs, max_epochs, min_lr=0, base_lr=0.001):
        self.optimizer = optimizer
        self.warmup_epochs = warmup_epochs
        self.max_epochs = max_epochs
        self.min_lr = min_lr
        self.base_lr = base_lr
        self.current_epoch = 0
    
    def step(self):
        self.current_epoch += 1
        lr = self.get_lr()
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr
        return lr
    
    def get_lr(self):
        if self.current_epoch <= self.warmup_epochs:
            # 线性预热
            return self.base_lr * self.current_epoch / self.warmup_epochs
        else:
            # 余弦退火
            progress = (self.current_epoch - self.warmup_epochs) / (self.max_epochs - self.warmup_epochs)
            return self.min_lr + (self.base_lr - self.min_lr) * 0.5 * (1 + torch.cos(torch.tensor(progress * 3.14159)))

# 完整训练循环示例（包含学习率调度）
def train_with_scheduler(model, train_loader, epochs=50):
    """使用学习率调度器的完整训练流程"""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
    
    # 使用学习率预热 + 余弦退火
    scheduler = WarmupCosineScheduler(
        optimizer, 
        warmup_epochs=5, 
        max_epochs=epochs,
        base_lr=0.001,
        min_lr=1e-6
    )
    
    history = {'train_loss': [], 'lr': []}
    
    for epoch in range(epochs):
        model.train()
        epoch_loss = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            epoch_loss += loss.item()
        
        # 更新学习率
        current_lr = scheduler.step()
        
        history['train_loss'].append(epoch_loss / len(train_loader))
        history['lr'].append(current_lr)
        
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss/len(train_loader):.4f}, LR: {current_lr:.6f}")
    
    return history
