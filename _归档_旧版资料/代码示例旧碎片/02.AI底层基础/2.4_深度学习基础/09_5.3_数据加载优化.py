# 高效数据加载器配置
train_loader = DataLoader(
    dataset=train_dataset,
    batch_size=64,
    shuffle=True,
    num_workers=4,      # 多进程加载
    pin_memory=True,    # 锁页内存，加速GPU传输
    prefetch_factor=2,  # 预取批次
    persistent_workers=True  # 保持worker进程
)
