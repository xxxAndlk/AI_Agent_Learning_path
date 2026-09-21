# 问题：训练loss下降但验证loss上升

# 解决方案1：增加正则化
lora_config = LoraConfig(
    lora_dropout=0.1,  # 增加dropout
)

# 解决方案2：早停
from transformers import EarlyStoppingCallback

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    callbacks=[EarlyStoppingCallback(early_stopping_patience=3)],
)

# 解决方案3：数据增强
def augment_data(text):
    """简单的数据增强"""
    # 同义词替换、回译等
    return augmented_text

# 解决方案4：减少训练轮数
# 小数据集通常1-3轮足够
training_args = TrainingArguments(
    num_train_epochs=2,  # 减少轮数
)
