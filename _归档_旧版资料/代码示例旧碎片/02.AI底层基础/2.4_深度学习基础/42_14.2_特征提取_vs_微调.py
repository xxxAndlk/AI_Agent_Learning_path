def feature_extraction_vs_finetuning():
    """特征提取和微调的对比"""
    
    model = models.resnet18(pretrained=True)
    
    # ===== 特征提取（Feature Extraction）=====
    # 思想：冻结预训练模型的所有层，只训练新添加的分类器
    # 适用场景：数据集较小，且与预训练数据分布相似
    
    # 1. 冻结所有层
    for param in model.parameters():
        param.requires_grad = False
    
    # 2. 替换分类头（这个默认requires_grad=True）
    num_features = model.fc.in_features
    model.fc = nn.Linear(num_features, 10)
    
    # 3. 只优化分类头
    optimizer = optim.Adam(model.fc.parameters(), lr=0.001)
    
    # 训练时，只有fc层的参数会更新
    # 前向传播正常，但反向传播只传到fc层为止
    
    # ===== 微调（Fine-tuning）=====
    # 思想：解冻部分或全部层，用较小的学习率训练
    # 适用场景：数据集较大，或与预训练数据有较大差异
    
    # 重新加载模型
    model = models.resnet18(pretrained=True)
    
    # 1. 解冻所有层（可以选只解冻后面的层）
    for param in model.parameters():
        param.requires_grad = True
    
    # 2. 使用较小的学习率（因为预训练参数已经很好）
    # 预训练层用小学习率，新层用大学习率
    optimizer = optim.AdamW([
        {'params': model.conv1.parameters(), 'lr': 1e-4},  # 浅层用更小lr
        {'params': model.layer2.parameters(), 'lr': 1e-4},
        {'params': model.layer3.parameters(), 'lr': 5e-5},
        {'params': model.layer4.parameters(), 'lr': 5e-5},
        {'params': model.fc.parameters(), 'lr': 1e-3},    # 新层用较大lr
    ], weight_decay=0.01)
    
    # ===== 渐进式解冻（Gradual Unfreezing）=====
    # 策略：先训练新层，然后逐步解冻预训练层
    
    def gradual_unfreeze_scheduler(epoch, model):
        """渐进式解冻调度器"""
        if epoch == 0:
            # 只训练新层
            for param in model.parameters():
                param.requires_grad = False
            for param in model.fc.parameters():
                param.requires_grad = True
        elif epoch == 5:
            # 解冻layer4
            for param in model.layer4.parameters():
                param.requires_grad = True
        elif epoch == 10:
            # 解冻layer3
            for param in model.layer3.parameters():
                param.requires_grad = True
        elif epoch == 15:
            # 解冻所有层
            for param in model.parameters():
                param.requires_grad = True


def complete_finetuning_example():
    """完整的微调训练流程"""
    
    # 1. 数据预处理（使用ImageNet的统计量）
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                           std=[0.229, 0.224, 0.225])
    ])
    
    # 2. 加载预训练模型
    model = models.resnet50(weights='IMAGENET1K_V1')
    
    # 替换分类头
    num_classes = 10
    model.fc = nn.Linear(model.fc.in_features, num_classes)
    
    # 3. 设置优化器（不同层用不同学习率）
    optimizer = optim.AdamW([
        {'params': model.conv1.parameters(), 'lr': 1e-4},
        {'params': model.layer2.parameters(), 'lr': 1e-4},
        {'params': model.layer3.parameters(), 'lr': 5e-5},
        {'params': model.layer4.parameters(), 'lr': 5e-5},
        {'params': model.fc.parameters(), 'lr': 1e-3},
    ], weight_decay=0.01)
    
    # 4. 学习率调度器
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=50)
    
    # 5. 训练循环
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    
    criterion = nn.CrossEntropyLoss()
    
    # ... 训练代码
