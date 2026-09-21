"""
vLLM高级配置与性能优化
"""

# 1. 预热模型
llm = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    enforce_eager=False,                 # CUDA图优化，默认开启
)

# 预热请求
warmup_prompts = ["warm up" for _ in range(2)]
llm.generate(warmup_prompts, SamplingParams(max_tokens=1))

# 2. 多GPU配置（张量并行）
llm_tp4 = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,              # 4卡并行
    pipeline_parallel_size=1,            # 流水线并行
    gpu_memory_utilization=0.9,
)

# 3. 分布式推理
# 启动多节点推理服务
# vllm serve meta-llama/Llama-2-70b-hf \
#     --tensor-parallel-size 4 \
#     --host 0.0.0.0 \
#     --port 8000

# 4. 内存优化配置
llm_optimized = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    # 量化配置
    quantization="awq",                  # AWQ量化
    kv_cache_dtype="fp8_e5m2",           # FP8 KV Cache
    
    # 内存管理
    max_num_seqs=512,                    # 增大并行数
    max_model_len=8192,                  # 支持更长序列
    
    # 计算优化
    enforce_eager=False,
    enable_chunked_prefill=True,         # 分块预填充
)

# 5. 推理结果解析
def parse_vllm_output(output):
    """解析vLLM输出"""
    result = {
        "text": output.outputs[0].text,
        "finish_reason": output.outputs[0].finish_reason,
        "token_ids": output.outputs[0].token_ids,
        "cumulative_logprob": output.outputs[0].cumulative_logprob,
    }
    
    # 获取每个token的log概率
    if output.outputs[0].logprobs:
        result["token_logprobs"] = [
            logprob.logprob if logprob else None
            for logprob in output.outputs[0].logprobs
        ]
    
    return result
