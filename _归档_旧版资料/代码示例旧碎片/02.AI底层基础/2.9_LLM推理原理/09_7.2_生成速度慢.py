# 解决方案1：使用KV Cache
model.generate(..., use_cache=True)

# 解决方案2：量化
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True  # 或 load_in_4bit=True
)

# 解决方案3：批量推理
# 一次处理多个请求
batch_inputs = tokenizer(prompts, return_tensors="pt", padding=True)
outputs = model.generate(**batch_inputs)

# 解决方案4：使用高效推理框架
# vLLM, TGI, TensorRT-LLM
