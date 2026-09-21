"""
llama.cpp部署
纯CPU/GPU推理，高效量化
"""

from llama_cpp import Llama

# 加载量化模型
llm = Llama(
    model_path="./models/llama-3.3-8b-instruct.Q4_K_M.gguf",
    
    # GPU配置
    n_gpu_layers=35,                      # 使用的GPU层数（0=只用CPU）
    
    # 上下文配置
    n_ctx=4096,                           # 上下文长度
    n_threads=8,                          # CPU线程数
    n_threads_batch=8,                    # 批处理线程数
    
    # 内存配置
    main_gpu="cuda:0",                    # 主GPU
    tensor_split=[0.6, 0.4],              # 多GPU分配比例
    
    # 生成参数
    temperature=0.7,
    top_p=0.95,
    repeat_penalty=1.1,
)

# 生成
output = llm(
    "写一个关于人工智能的短文：",
    max_tokens=500,
    temperature=0.8,
    stop=["###"],                         # 停止词
    echo=False,                           # 不回显输入
)

print(output["choices"][0]["text"])

# 流式生成
print("流式输出：")
stream = llm(
    "继续这个故事：从前有座山，",
    max_tokens=200,
    stream=True,
)

for chunk in stream:
    print(chunk["choices"][0]["text"], end="", flush=True)

# 批量推理
prompts = [
    "问题1：什么是机器学习？",
    "问题2：解释深度学习：",
    "问题3：神经网络如何工作？",
]

# llama.cpp不支持原生批量，使用循环
results = [llm(p, max_tokens=100) for p in prompts]

# 性能优化配置
llm_optimized = Llama(
    model_path="./models/llama-3.3-8b-instruct.Q4_K_M.gguf",
    
    # 性能优化选项
    use_mmap=True,                        # 内存映射
    use_mlock=False,                      # 锁定内存
    
    # KV Cache优化
    n_cache_seq_len=512,                  # 缓存序列长度
    
    # 推测解码（需要两个模型）
    # lora_adapter="path/to/lora",        # LoRA适配器
)
