"""
vLLM流式生成
vLLM原生支持流式输出
"""

from vllm import LLM, SamplingParams

# 初始化
llm = LLM("meta-llama/Llama-2-7b-chat-hf")

# 方法1: 使用generate的streaming参数
sampling_params = SamplingParams(
    max_tokens=200,
    temperature=0.7,
    stream=True,                          # 启用流式输出
)

prompt = "写一个关于春天的诗："

# 生成器方式
for output in llm.generate([prompt], sampling_params):
    # 每次迭代输出一个token
    if output.outputs[0].text:
        print(output.outputs[0].text, end="", flush=True)

# 方法2: 使用AsyncLLMEngine
import asyncio

async def async_stream_generate():
    """异步流式生成"""
    from vllm import AsyncLLMEngine
    from vllm.sampling_params import SamplingParams
    
    engine = AsyncLLMEngine(
        model="meta-llama/Llama-2-7b-chat-hf",
        trust_remote_code=True,
    )
    
    sampling_params = SamplingParams(
        max_tokens=200,
        temperature=0.7,
    )
    
    # 异步生成
    async for output in engine.generate(prompt, sampling_params):
        if output.outputs[0].text:
            print(output.outputs[0].text, end="", flush=True)

# 运行
# asyncio.run(async_stream_generate())
