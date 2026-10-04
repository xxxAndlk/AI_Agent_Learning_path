"""
vLLM动态批处理配置详解
"""

# 不同的批处理策略
llm_fcfs = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    scheduler_config={
        "policy": "fcfs",                 # 先来先服务
        "max_num_seqs": 256,              # 最大序列数
    },
)

llm_priority = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    scheduler_config={
        "policy": "priority",             # 优先级调度
        "priority_levels": 3,             # 优先级级别
    },
)

# 延迟容忍度配置
llm_with_latency = LLM(
    model="meta-llama/Llama-2-7b-chat-hf",
    scheduling_config={
        "max_num_seqs": 128,
        "max_model_len": 4096,
    },
    engine_config={
        "decoding_config": {
            "decoding_params": {
                "multi_modal_decoding": {
                    "enable": True,
                },
            },
        },
    },
)

# 性能监控
def benchmark_batching():
    """测试批处理性能"""
    import time
    
    # 单请求延迟测试
    single_prompt = "写一个关于人工智能的短文。"
    start = time.time()
    outputs = llm.generate([single_prompt], sampling_params)
    single_latency = time.time() - start
    
    # 批量请求延迟测试
    batch_prompts = [single_prompt] * 10
    start = time.time()
    outputs = llm.generate(batch_prompts, sampling_params)
    batch_latency = time.time() - start
    
    print(f"单请求延迟: {single_latency:.3f}s")
    print(f"10请求批量延迟: {batch_latency:.3f}s")
    print(f"吞吐量提升: {single_latency * 10 / batch_latency:.2f}x")
