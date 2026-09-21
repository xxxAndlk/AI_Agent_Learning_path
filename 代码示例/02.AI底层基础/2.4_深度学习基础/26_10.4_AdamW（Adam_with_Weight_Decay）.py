# AdamW vs Adam + L2正则化
# AdamW（推荐用于Transformer等现代架构）
optimizer_adamw = optim.AdamW(
    model.parameters(),
    lr=0.001,
    weight_decay=0.01,  # 权重衰减系数
    betas=(0.9, 0.999)
)

# 等价的Adam + L2正则（不推荐）
optimizer_adam_l2 = optim.Adam(
    model.parameters(),
    lr=0.001,
    weight_decay=0.01  # 这里实际上是把weight_decay加到梯度上
)
# 区别：AdamW在更新时直接减去weight_decay * lr * param
# 而Adam + L2是把weight_decay项加到梯度中再更新
