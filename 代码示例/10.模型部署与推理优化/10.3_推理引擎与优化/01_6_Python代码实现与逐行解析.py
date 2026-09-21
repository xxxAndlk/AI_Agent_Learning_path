# 1. vLLM使用示例（需要安装: pip install vllm）
"""
vLLM是一个高吞吐量的大模型推理引擎，核心特性：
1. PagedAttention: 高效的KV Cache管理，减少内存浪费
2. Continuous Batching: 动态批处理，提高GPU利用率
3. 量化支持: 内置AWQ、GPTQ等量化方案
"""

def vllm_inference_example():
    """2. vLLM推理示例
    
    展示vLLM的基本使用方法，包括模型加载和批量推理
    需要安装: pip install vllm
    注意: vLLM需要Linux环境和CUDA支持的GPU
    """
    try:
        # 3. 导入vLLM核心类
        from vllm import LLM, SamplingParams
        
        # 4. 加载模型
        # LLM类是vLLM的核心，负责模型加载和推理管理
        # 支持HuggingFace模型ID或本地路径
        print("正在加载模型...")
        llm = LLM(
            model="meta-llama/Llama-3.1-8B-Instruct",  # 5. 模型名称
            tensor_parallel_size=1,             # 6. GPU数量，1表示单GPU
            gpu_memory_utilization=0.9,         # 7. GPU内存使用率
            max_model_len=4096                  # 8. 最大序列长度
        )
        
        # 9. 定义采样参数
        # SamplingParams控制文本生成的随机性和长度
        sampling_params = SamplingParams(
            temperature=0.7,                    # 10. 温度参数（0-2）
                                                # 低温度更确定性，高温度更随机
            top_p=0.95,                         # 11. 核采样概率
            max_tokens=256                      # 12. 最大生成token数
        )
        
        # 13. 准备提示词列表
        prompts = [
            "人工智能的未来发展",
            "请介绍一下深度学习",
            "什么是机器学习？"
        ]
        
        # 14. 批量推理
        # vLLM会自动进行批处理优化
        print("开始推理...")
        outputs = llm.generate(prompts, sampling_params)
        
        # 15. 打印结果
        for i, output in enumerate(outputs):
            print(f"\n--- 提示 {i+1} ---")
            print(f"输入: {prompts[i]}")
            # 16. 获取生成的文本
            print(f"输出: {output.outputs[0].text}")
        
    except ImportError:
        # 17. 处理未安装vLLM的情况
        print("请先安装vLLM: pip install vllm")
        print("注意: vLLM需要Linux环境和CUDA支持的GPU")

def batch_inference_optimization():
    """18. 批量推理优化示例
    
    通过动态批处理（Dynamic Batching）提高吞吐量
    对比串行推理和批处理推理的性能差异
    """
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import time
    
    # 19. 加载模型（使用小模型演示）
    # 使用gpt2作为示例，实际应用中可以替换为其他模型
    model_name = "gpt2"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # 20. 设置pad token（GPT2默认没有pad token）
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # 21. 将模型移到GPU（如有）
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device)
    model.eval()
    
    # 22. 准备多个提示词
    prompts = [
        "人工智能是",
        "深度学习的应用包括",
        "机器学习算法有",
        "神经网络可以",
        "自然语言处理技术"
    ]
    
    # 23. 方法1：串行推理（低效）
    # 逐个处理每个提示词
    print("方法1: 串行推理")
    start = time.time()
    with torch.no_grad():
        for prompt in prompts:          # 24. 遍历每个提示词
            # 25. 逐个tokenize
            inputs = tokenizer(prompt, return_tensors="pt").to(device)
            # 26. 逐个生成
            outputs = model.generate(
                **inputs,
                max_new_tokens=20,
                do_sample=False
            )
    serial_time = time.time() - start
    print(f"串行推理时间: {serial_time:.3f}s")
    
    # 27. 方法2：批处理推理（高效）
    print("\n方法2: 批处理推理")
    start = time.time()
    
    # 28. 对所有提示词一起编码
    # 使用padding=True将不同长度的提示词填充到相同长度
    # truncation=True截断超过max_length的输入
    inputs = tokenizer(
        prompts,
        return_tensors="pt",
        padding=True,                       # 29. 填充到相同长度
        truncation=True,
        max_length=50
    ).to(device)
    
    # 30. 批量生成
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=20,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id  # 31. 指定pad token id
        )
    
    batch_time = time.time() - start
    print(f"批处理推理时间: {batch_time:.3f}s")
    
    # 32. 批量解码结果
    results = tokenizer.batch_decode(outputs, skip_special_tokens=True)
    
    # 33. 计算并打印性能提升
    print(f"\n吞吐量提升: {serial_time/batch_time:.2f}x")
    print("\n生成结果:")
    for i, result in enumerate(results):
        print(f"{i+1}. {result}")

if __name__ == "__main__":
    # 34. 运行批量推理优化示例
    batch_inference_optimization()
