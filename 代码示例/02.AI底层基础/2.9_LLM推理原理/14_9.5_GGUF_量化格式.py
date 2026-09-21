"""
GGUF格式说明与llama.cpp使用
GGUF是llama.cpp推出的高效量化格式，支持多种精度组合
"""

# GGUF量化类型说明
"""
GGUF量化精度：
- Q2_K: 2位量化，K表示使用K-分组
- Q3_K_S/M/L: 3位量化，不同分组大小
- Q4_0/Q4_1: 4位量化
- Q4_K: 4位量化，K分组
- Q5_0/Q5_1/Q5_K: 5位量化
- Q6_K: 6位量化
- Q8_0: 8位量化

推荐配置：
- 追求质量：Q5_K_M
- 平衡选择：Q4_K_M
- 追求速度：Q3_K_M
"""

# 使用llama.cpp的Python绑定
from llama_cpp import Llama

# 加载GGUF量化模型
llm = Llama(
    model_path="./models/llama-3.3-8b-instruct.Q4_K_M.gguf",
    n_gpu_layers=-1,                      # 使用GPU加速
    n_ctx=4096,                           # 上下文长度
    n_threads=8,                          # CPU线程数
    verbose=False,
)

# 生成
output = llm(
    "写一个关于人工智能的短故事：",
    max_tokens=500,
    temperature=0.8,
    top_p=0.95,
)

print(output["choices"][0]["text"])
