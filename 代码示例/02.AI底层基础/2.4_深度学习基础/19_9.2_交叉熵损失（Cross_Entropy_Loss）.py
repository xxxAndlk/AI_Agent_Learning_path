# 多分类交叉熵损失
# 适用于互斥的分类任务（如MNIST手写数字识别）
criterion = nn.CrossEntropyLoss()

# 模拟batch=4, 类别数=10的输出（未经过softmax）
logits = torch.randn(4, 10)  # 每个样本10个类别的原始分数
# 真实标签（类别索引）
targets = torch.tensor([3, 7, 1, 5])

loss = criterion(logits, targets)
print(f"CrossEntropy Loss: {loss.item():.4f}")

# 使用softmax + NLLLoss的等价写法
log_probs = torch.log_softmax(logits, dim=1)  # 先转成log概率
nll_loss = nn.NLLLoss()
loss2 = nll_loss(log_probs, targets)
print(f"NLLLoss: {loss2.item():.4f}")
print(f"两者相等: {torch.isclose(loss, loss2)}")

# 二分类交叉熵损失（BCELoss）
criterion_bce = nn.BCEWithLogitsLoss()

# 二分类：模拟sigmoid之前的logit输出
logits_binary = torch.randn(4, 1)
# 二分类的真实标签（0或1）
targets_binary = torch.tensor([[1.], [0.], [1.], [0.]])

loss_bce = criterion_bce(logits_binary, targets_binary)
print(f"BCE Loss: {loss_bce.item():.4f}")

# 如果已经使用sigmoid激活，需要使用BCELoss
sigmoid_output = torch.sigmoid(logits_binary)
criterion_bce_raw = nn.BCELoss()
loss_bce_raw = criterion_bce_raw(sigmoid_output, targets_binary)
print(f"BCE Loss (raw): {loss_bce_raw.item():.4f}")
