"""
vLLM投机解码实现
vLLM 0.3+ 支持投机解码
"""

from vllm import LLM, SamplingParams, DecodingMetadata

# 加载主模型和草稿模型
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",      # 主模型
    speculative_model="meta-llama/Llama-2-7b-hf",  # 草稿模型
    num_speculative_tokens=5,               # 每次投机生成5个token
    tensor_parallel_size=4,
)

sampling_params = SamplingParams(
    temperature=0.0,                         # 使用贪婪解码
    max_tokens=256,
)

# 生成（自动使用投机解码）
prompt = "写一个关于深度学习的详细教程："
output = llm.generate([prompt], sampling_params)

print(f"生成的文本: {output[0].outputs[0].text}")

# 手动配置投机解码参数
speculative_llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    speculative_model="meta-llama/Llama-2-7b-hf",
    num_speculative_tokens=5,
    speculative_max_model_len=2048,         # 草稿模型最大长度
)
