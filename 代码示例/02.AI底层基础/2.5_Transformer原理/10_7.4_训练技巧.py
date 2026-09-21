# 1. 学习率预热 (Learning Rate Warmup)
def get_lr_scheduler(optimizer, warmup_steps, d_model):
    """Noam学习率调度器（原始Transformer）"""
    def lr_lambda(step):
        if step == 0:
            return 1e-8
        return min(step ** -0.5, step * warmup_steps ** -1.5) * d_model ** -0.5
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)

# 2. 标签平滑 (Label Smoothing)
class LabelSmoothing(nn.Module):
    def __init__(self, vocab_size, padding_idx, smoothing=0.1):
        super().__init__()
        self.criterion = nn.KLDivLoss(reduction='sum')
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.vocab_size = vocab_size
    
    def forward(self, pred, target):
        # 创建平滑标签
        smooth_target = torch.zeros_like(pred)
        smooth_target.fill_(self.smoothing / (self.vocab_size - 2))
        smooth_target.scatter_(1, target.unsqueeze(1), self.confidence)
        smooth_target[:, self.padding_idx] = 0
        mask = (target == self.padding_idx)
        smooth_target[mask] = 0
        return self.criterion(pred, smooth_target)
