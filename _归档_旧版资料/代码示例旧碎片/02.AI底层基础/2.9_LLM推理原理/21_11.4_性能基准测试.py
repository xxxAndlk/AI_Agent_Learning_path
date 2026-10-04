"""
vLLM性能基准测试
"""

import time
import torch
from vllm import LLM, SamplingParams

def benchmark_vllm():
    """vLLM性能测试"""
    
    # 初始化
    llm = LLM(
        model="meta-llama/Llama-2-7b-chat-hf",
        tensor_parallel_size=1,
        gpu_memory_utilization=0.85,
    )
    
    sampling_params = SamplingParams(
        max_tokens=256,
        temperature=0.0,
    )
    
    # 测试不同的并发级别
    test_concurrency = [1, 2, 4, 8, 16, 32]
    prompt = "写一个关于人工智能的详细说明：" + "解释" * 100
    
    results = []
    
    for concurrency in test_concurrency:
        prompts = [prompt] * concurrency
        
        # 预热
        llm.generate(prompts[:2], sampling_params)
        torch.cuda.synchronize()
        
        # 正式测试
        start = time.time()
        outputs = llm.generate(prompts, sampling_params)
        torch.cuda.synchronize()
        
        elapsed = time.time() - start
        total_tokens = sum(len(o.outputs[0].token_ids) for o in outputs)
        
        results.append({
            "concurrency": concurrency,
            "total_time": elapsed,
            "throughput": total_tokens / elapsed,
            "latency": elapsed / concurrency,
            "avg_tokens_per_request": total_tokens / concurrency,
        })
        
        print(f"并发{concurrency:2d}: "
              f"总时间{elapsed:.2f}s, "
              f"吞吐量{total_tokens/elapsed:.1f} tokens/s")
    
    return results

# 预期结果（7B模型，A100-40GB）
"""
并发数 │ 总时间 │ 吞吐量   │ 平均延迟
───────┼────────┼──────────┼─────────
1      │ 1.2s   │ 213/s    │ 1.2s
2      │ 1.4s   │ 366/s    │ 0.7s
4      │ 1.8s   │ 569/s    │ 0.45s
8      │ 2.5s   │ 819/s    │ 0.31s
16     │ 4.2s   │ 975/s    │ 0.26s
32     │ 7.8s   │ 1051/s   │ 0.24s
"""
