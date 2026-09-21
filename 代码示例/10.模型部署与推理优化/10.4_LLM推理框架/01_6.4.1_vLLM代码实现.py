"""
1. vLLM推理框架完整示例
展示如何使用vLLM部署大语言模型进行高效推理
需要安装: pip install vllm
"""

import os                           # 2. 操作系统接口，用于环境变量管理
from typing import List, Dict       # 3. 类型提示，提供更好的代码可读性

def vllm_basic_example():
    """4. vLLM基础推理示例
    
    展示vLLM的基本使用方法，包括模型加载、参数配置和批量推理
    """
    try:
        # 5. 导入vLLM核心模块
        from vllm import LLM, SamplingParams
        
        print("=" * 60)
        print("vLLM基础推理示例")
        print("=" * 60)
        
        # 6. 步骤1: 初始化LLM引擎
        # LLM类是vLLM的核心类，负责模型加载和推理管理
        llm = LLM(
            model="Qwen/Qwen2.5-0.5B-Instruct",  # 7. 模型名称，支持HuggingFace格式
            tensor_parallel_size=1,               # 8. 张量并行数，多GPU时设为GPU数量
            gpu_memory_utilization=0.9,           # 9. GPU显存利用率，0.9表示使用90%显存
            max_model_len=4096,                   # 10. 最大序列长度，影响KV Cache大小
            trust_remote_code=True,               # 11. 是否信任远程代码（部分模型需要）
            dtype="auto",                         # 12. 数据类型，auto自动选择最优
        )
        print("✅ 模型加载完成")
        
        # 13. 步骤2: 配置采样参数
        # SamplingParams控制文本生成的随机性和长度
        sampling_params = SamplingParams(
            temperature=0.7,                      # 14. 温度参数，控制随机性（0-2）
                                                    # 低温度(0.3)更确定，高温度(1.0+)更随机
            top_p=0.9,                            # 15. 核采样参数，保留累积概率为p的token
            top_k=50,                             # 16. Top-K采样，只从概率最高的K个token中采样
            max_tokens=256,                       # 17. 最大生成token数
            frequency_penalty=0.0,                # 18. 频率惩罚，减少重复词（0-2）
            presence_penalty=0.0,                 # 19. 存在惩罚，鼓励话题多样性（0-2）
            stop=["<|endoftext|>", "###"],       # 20. 停止词，遇到这些词时停止生成
        )
        
        # 21. 步骤3: 准备输入提示词
        # vLLM支持批量推理，可以一次处理多个请求
        prompts = [
            "请用一句话解释什么是机器学习：",
            "Python语言的主要特点是什么？",
            "深度学习和机器学习有什么区别？",
        ]
        
        # 22. 步骤4: 执行批量推理
        # vLLM会自动进行批处理优化，提高GPU利用率
        print("\n开始推理...")
        outputs = llm.generate(prompts, sampling_params)
        
        # 23. 步骤5: 处理并输出结果
        # outputs是一个RequestOutput对象列表
        for i, output in enumerate(outputs):
            print(f"\n--- 结果 {i+1} ---")
            print(f"输入: {output.prompt}")
            print(f"输出: {output.outputs[0].text}")
            print(f"生成token数: {len(output.outputs[0].token_ids)}")
        
        print("\n✅ 推理完成")
        
    except ImportError:
        print("⚠️ 请先安装vLLM: pip install vllm")
        print("注意: vLLM需要Linux环境和CUDA支持的GPU")

def vllm_api_server_example():
    """24. vLLM API服务示例
    
    展示如何启动vLLM的OpenAI兼容API服务
    服务启动命令:
    vllm serve \
        --model Qwen/Qwen2.5-0.5B-Instruct \
        --host 0.0.0.0 \
        --port 8000
    """
    try:
        import openai                      # 25. OpenAI客户端库
        
        print("\n" + "=" * 60)
        print("vLLM API服务调用示例")
        print("=" * 60)
        
        # 26. 创建OpenAI客户端，指向vLLM服务地址
        client = openai.OpenAI(
            base_url="http://localhost:8000/v1",  # vLLM服务地址
            api_key="dummy-key"                    # vLLM不需要真实API key
        )
        
        # 27. 发送Chat Completion请求
        # 完全兼容OpenAI的Chat API格式
        response = client.chat.completions.create(
            model="Qwen/Qwen2.5-0.5B-Instruct",   # 模型名称
            messages=[
                {"role": "system", "content": "你是一个有帮助的AI助手。"},
                {"role": "user", "content": "请解释什么是Transformer模型？"}
            ],
            temperature=0.7,                       # 温度参数
            max_tokens=256,                        # 最大生成token数
            stream=False,                          # 是否流式输出
        )
        
        # 28. 输出结果
        print(f"\n回复: {response.choices[0].message.content}")
        print(f"使用token数: {response.usage.total_tokens}")
        
    except ImportError:
        print("⚠️ 请先安装openai: pip install openai")

def vllm_streaming_example():
    """29. vLLM流式输出示例
    
    展示如何使用vLLM进行流式文本生成
    """
    try:
        import openai
        
        print("\n" + "=" * 60)
        print("vLLM流式输出示例")
        print("=" * 60)
        
        client = openai.OpenAI(
            base_url="http://localhost:8000/v1",
            api_key="dummy-key"
        )
        
        # 30. 发送流式请求
        # stream=True 启用流式输出
        stream = client.chat.completions.create(
            model="Qwen/Qwen2.5-0.5B-Instruct",
            messages=[
                {"role": "user", "content": "请写一首关于春天的短诗。"}
            ],
            temperature=0.8,
            max_tokens=128,
            stream=True,                           # 31. 启用流式输出
        )
        
        print("\n流式输出: ")
        # 32. 逐块处理流式响应
        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                print(chunk.choices[0].delta.content, end="", flush=True)
        
        print("\n\n✅ 流式输出完成")
        
    except Exception as e:
        print(f"⚠️ 流式输出示例需要vLLM服务运行: {e}")

# vLLM性能对比表
"""
| 特性 | vLLM | HuggingFace Transformers |
|------|------|-------------------------|
| **吞吐量** | 10-20x更高 | 基准 |
| **内存效率** | 高（PagedAttention） | 低（预分配） |
| **批处理** | 动态批处理 | 静态批处理 |
| **API兼容** | OpenAI兼容 | 自定义API |
| **量化支持** | AWQ, GPTQ, FP8 | 部分支持 |
| **多GPU** | 张量并行 | 需要额外配置 |
"""

if __name__ == "__main__":
    vllm_basic_example()
