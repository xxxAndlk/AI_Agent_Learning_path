# 解决方案1：学习率预热
training_args = TrainingArguments(
    warmup_steps=100,
    warmup_ratio=0.1,
)

# 解决方案2：梯度裁剪
training_args = TrainingArguments(
    max_grad_norm=1.0,  # 梯度裁剪
)

# 解决方案3：调整学习率
# LoRA通常使用较高学习率
training_args = TrainingArguments(
    learning_rate=2e-4,  # LoRA推荐
)

# 解决方案4：使用更稳定的优化器
from transformers import get_cosine_schedule_with_warmup

scheduler = get_cosine_schedule_with_warmup(
    optimizer,
    num_warmup_steps=100,
    num_training_steps=total_steps,
)
