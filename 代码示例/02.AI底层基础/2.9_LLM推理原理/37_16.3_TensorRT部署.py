"""
TensorRT-LLM部署
"""

# 安装: pip install tensorrt_llm

from tensorrt_llm import LLM
from tensorrt_llm.runtime import SamplingParams

# 初始化TensorRT-LLM
llm = LLM(
    model_dir="/trt_model/llama-7b",
    max_tokens=512,
    beam_width=1,
)

# 生成
sampling_params = SamplingParams(
    temperature=0.7,
    top_p=0.9,
    max_tokens=200,
)

output = llm.generate(
    ["写一个关于Python的教程："],
    sampling_params,
)

print(output[0].outputs[0].text)

# 量化模型构建
"""
# 构建INT8量化模型
trtllm build --model_type llama \
    --model_name meta-llama/Llama-2-7b-chat-hf \
    --quantization int8 \
    --output_dir /trt_model/llama-7b-int8
"""

# 使用Python API进行模型量化
from tensorrt_llm.builder import Builder

Builder().build_model(
    model_config=...,
    build_config=Builder.BuildConfig(
        quantization="fp8",
        opt_level=...,
    ),
)
