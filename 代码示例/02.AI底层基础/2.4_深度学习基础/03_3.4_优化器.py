# 不同优化器的学习率调整策略
optimizers = {
    'SGD': optim.SGD(model.parameters(), lr=0.1, momentum=0.9),
    'Adam': optim.Adam(model.parameters(), lr=0.001),
    'AdamW': optim.AdamW(model.parameters(), lr=0.001, weight_decay=0.01)
}
