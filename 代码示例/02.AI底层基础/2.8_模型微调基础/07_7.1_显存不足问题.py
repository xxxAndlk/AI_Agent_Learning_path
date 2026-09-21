# 问题：7B模型全量微调需要约28GB显存

# 解决方案1：使用LoRA
# 显存降低到约16GB

# 解决方案2：使用QLoRA
# 显存降低到约6GB
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
)

# 解决方案3：梯度累积
training_args = TrainingArguments(
    per_device_train_batch_size=1,      # 减小batch
    gradient_accumulation_steps=16,     # 累积16步
)

# 解决方案4：DeepSpeed ZeRO
# 使用DeepSpeed进行显存优化
training_args = TrainingArguments(
    deepspeed="ds_config.json",  # DeepSpeed配置
)
