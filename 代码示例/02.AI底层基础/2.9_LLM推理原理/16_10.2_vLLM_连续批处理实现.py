"""
vLLM连续批处理使用
vLLM实现了PagedAttention和连续批处理
"""

from vllm import LLM, SamplingParams

# 初始化vLLM引擎
llm = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    tensor_parallel_size=1,               # GPU数量
    gpu_memory_utilization=0.9,           # GPU内存使用比例
    max_num_seqs=256,                     # 最大并行序列数
    enforce_eager=False,                  # 使用CUDA图优化
)

# 定义采样参数
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.95,
    max_tokens=512,
    stop=None,
)

# 批量请求
prompts = [
    "写一个关于机器学习的简介：",
    "解释什么是深度学习：",
    "介绍一下神经网络的工作原理：",
    "什么是自然语言处理？",
    "机器学习和人工智能有什么区别？",
]

# 批量推理
outputs = llm.generate(prompts, sampling_params)

# 处理结果
for i, output in enumerate(outputs):
    print(f"请求 {i+1}: {output.outputs[0].text[:100]}...")
