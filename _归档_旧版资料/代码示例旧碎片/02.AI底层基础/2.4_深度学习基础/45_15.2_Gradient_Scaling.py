from torch.amp import autocast, GradScaler

class MixedPrecisionTrainer:
    """混合精度训练器"""
    
    def __init__(self, model, optimizer, criterion, device='cuda'):
        self.model = model.to(device)
        self.optimizer = optimizer
        self.criterion = criterion
        self.device = device
        
        # 创建GradScaler
        # init_scale: 初始缩放因子，通常设为2^16
        # growth_factor: 每次成功更新后放大倍数
        # backoff_factor: 梯度溢出后缩小倍数
        # growth_interval: 连续成功更新的次数阈值
        self.scaler = GradScaler(
            init_scale=65536,  # 2^16
            growth_factor=2.0,
            backoff_factor=0.5,
            growth_interval=2000
        )
    
    def train_step(self, data, target):
        """单步训练"""
        
        # 1. 前向传播（自动使用FP16）
        # autocast会自动将计算转换为FP16/BF16
        with autocast("cuda", dtype=torch.float16):  # 或 torch.bfloat16
            output = self.model(data)
            loss = self.criterion(output, target)
        
        # 2. 反向传播
        # scaler.scale() 放大loss用于反向传播
        self.scaler.scale(loss).backward()
        
        # 3. 梯度裁剪（scaler处理后的梯度）
        self.scaler.unscale_(self.optimizer)
        torch.nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
        
        # 4. 参数更新
        # scaler.step() 会先缩小梯度，再更新参数
        self.scaler.step(self.optimizer)
        
        # 5. 更新缩放因子
        self.scaler.update()
        
        return loss.item()


def complete_mixed_precision_training():
    """完整的混合精度训练流程"""
    
    # 模型
    model = nn.Linear(100, 10).cuda()
    
    # 优化器
    optimizer = optim.AdamW(model.parameters(), lr=0.001)
    
    # 损失函数
    criterion = nn.CrossEntropyLoss()
    
    # GradScaler
    scaler = GradScaler()
    
    # 训练循环
    for epoch in range(10):
        for batch_idx in range(100):
            data = torch.randn(32, 100).cuda()
            target = torch.randint(0, 10, (32,)).cuda()
            
            optimizer.zero_grad()
            
            # 混合精度前向传播
            with autocast("cuda", dtype=torch.float16):
                output = model(data)
                loss = criterion(output, target)
            
            # 反向传播（放大梯度）
            scaler.scale(loss).backward()
            
            # 梯度裁剪
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            # 参数更新（处理梯度溢出）
            scaler.step(optimizer)
            scaler.update()
            
            # 可选：手动调整学习率
            # scaler.get_scale() 获取当前缩放因子
            
        print(f"Epoch {epoch}, Loss: {loss.item():.4f}")


def automatic_mixed_precision():
    """自动混合精度（AMP）
    
    PyTorch 1.10+ 支持自动选择精度
    """
    # 自动选择最佳精度
    # 在支持的GPU上自动使用TF32
    with autocast("cuda", enabled=True):  # 启用自动混合精度
        # 第一次前向传播确定精度
        pass
    
    # 手动指定BF16
    if torch.cuda.is_available() and torch.cuda.is_bf16_supported():
        with autocast("cuda", dtype=torch.bfloat16):
            pass
    
    # 自定义cast添加
    def custom_autocast(enabled=True):
        return torch.amp.autocast(
            enabled=enabled,
            dtype=torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
        )
