"""
bitsandbytes 量化配置
实现模型加载时的INT8/INT4量化
"""

from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
import torch

# INT8量化配置
int8_config = BitsAndBytesConfig(
    load_in_8bit=True,                    # 加载为INT8
)

# INT4量化配置
int4_config = BitsAndBytesConfig(
    load_in_4bit=True,                    # 加载为INT4
    bnb_4bit_quant_type="nf4",            # NF4量化类型
    bnb_4bit_compute_dtype=torch.float16, # 计算时使用FP16
    bnb_4bit_use_double_quant=True,       # 双重量化进一步压缩
)

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    "meta-llama/Llama-2-7b-hf",
    quantization_config=int4_config,
    device_map="auto",                    # 自动分配到可用设备
    trust_remote_code=True,
)

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

# 推理使用
def generate_with_quantized_model(prompt: str, max_new_tokens: int = 100):
    """使用量化模型生成"""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.9,
        )
    
    return tokenizer.decode(outputs[0], skip_special_tokens=True)
