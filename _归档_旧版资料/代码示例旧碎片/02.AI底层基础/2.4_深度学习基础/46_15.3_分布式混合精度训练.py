def distributed_mixed_precision():
    """分布式环境下的混合精度训练"""
    
    # 使用DistributedDataParallel时的混合精度
    model = nn.Linear(100, 10).cuda()
    model = nn.parallel.DistributedDataParallel(model)
    
    optimizer = optim.AdamW(model.parameters(), lr=0.001)
    scaler = GradScaler()
    criterion = nn.CrossEntropyLoss()
    
    # 训练步骤
    data = torch.randn(32, 100).cuda()
    target = torch.randint(0, 10, (32,)).cuda()
    
    optimizer.zero_grad()
    
    with autocast("cuda", dtype=torch.float16):
        output = model(data)
        loss = criterion(output, target)
    
    scaler.scale(loss).backward()
    scaler.unscale_(optimizer)
    
    # 跨GPU梯度同步后裁剪
    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
    
    scaler.step(optimizer)
    scaler.update()
