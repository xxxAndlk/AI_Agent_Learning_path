"""
vLLM安装与基础使用
"""

# 安装vLLM
# pip install vllm

# 基础使用
from vllm import LLM, SamplingParams

# 初始化引擎
llm = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    trust_remote_code=True,
    # GPU配置
    tensor_parallel_size=1,              # 张量并行GPU数
    gpu_memory_utilization=0.85,         # GPU内存利用率
    max_model_len=4096,                  # 最大模型长度
    
    # KV Cache配置
    kv_cache_dtype="auto",               # KV Cache数据类型
    enforce_eager=False,                 # 启用CUDA图优化
    
    # 调度配置
    scheduler_config={
        "max_num_seqs": 256,             # 最大并行序列数
    },
)

# 采样参数
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=512,
    stop=["###"],                        # 停止符
    logprobs=1,                          # 返回log概率
)

# 单次生成
prompt = "写一个关于Python的简介："
outputs = llm.generate([prompt], sampling_params)

for output in outputs:
    print(f"生成的文本: {output.outputs[0].text}")
    print(f"Log概率: {output.outputs[0].logprobs}")
