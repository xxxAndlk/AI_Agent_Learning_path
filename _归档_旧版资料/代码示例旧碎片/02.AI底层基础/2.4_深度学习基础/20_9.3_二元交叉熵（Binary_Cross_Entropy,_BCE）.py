# 方式1：使用BCEWithLogitsLoss（推荐，数值更稳定）
criterion = nn.BCEWithLogitsLoss()

# logits: 模型输出的原始分数（未经过sigmoid）
logits = torch.tensor([2.1, -0.8, 0.5, -1.2])
# targets: 真实标签（0或1）
targets = torch.tensor([1., 0., 1., 0.])

loss = criterion(logits, targets)
print(f"BCEWithLogitsLoss: {loss.item():.4f}")

# 方式2：手动实现BCE
def bce_loss(logits, targets):
    """手动实现二元交叉熵损失"""
    # 添加eps防止log(0)
    eps = 1e-7
    probs = torch.sigmoid(logits)
    # L = -[y*log(p) + (1-y)*log(1-p)]
    loss = -targets * torch.log(probs + eps) - (1 - targets) * torch.log(1 - probs + eps)
    return torch.mean(loss)

manual_bce = bce_loss(logits, targets)
print(f"手动BCE: {manual_bce.item():.4f}")
