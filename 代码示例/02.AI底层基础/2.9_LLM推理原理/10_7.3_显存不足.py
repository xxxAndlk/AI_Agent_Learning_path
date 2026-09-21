# 解决方案1：模型量化
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.float16,
)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    quantization_config=bnb_config,
    device_map="auto"
)

# 解决方案2：限制最大长度
max_new_tokens = 512  # 适当减少

# 解决方案3：使用PagedAttention (vLLM)
# 自动管理KV Cache内存
