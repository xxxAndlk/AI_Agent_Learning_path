# 学习率查找器
def find_lr(model, train_loader, min_lr=1e-7, max_lr=1, num_iter=100):
    losses = []
    lrs = []
    optimizer = optim.Adam(model.parameters(), lr=min_lr)
    scheduler = optim.lr_scheduler.ExponentialLR(optimizer, gamma=(max_lr/min_lr)**(1/num_iter))
    
    model.train()
    iterator = iter(train_loader)
    for i in range(num_iter):
        try:
            data, target = next(iterator)
        except StopIteration:
            iterator = iter(train_loader)
            data, target = next(iterator)
        
        optimizer.zero_grad()
        output = model(data)
        loss = F.cross_entropy(output, target)
        loss.backward()
        optimizer.step()
        
        losses.append(loss.item())
        lrs.append(optimizer.param_groups[0]['lr'])
        scheduler.step()
    
    return lrs, losses  # 绘制lr vs loss曲线，找最优lr
