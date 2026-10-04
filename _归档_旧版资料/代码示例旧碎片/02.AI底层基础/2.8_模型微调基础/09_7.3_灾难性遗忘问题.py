# 问题：微调后模型在原任务上表现下降

# 解决方案1：使用较小的学习率
training_args = TrainingArguments(
    learning_rate=1e-5,  # 降低学习率
)

# 解决方案2：混合训练数据
mixed_data = domain_data + general_data  # 混合领域数据和通用数据

# 解决方案3：LoRA（天然缓解）
# LoRA只更新增量，原始权重保持不变

# 解决方案4：多任务微调
# 同时在多个任务上微调
