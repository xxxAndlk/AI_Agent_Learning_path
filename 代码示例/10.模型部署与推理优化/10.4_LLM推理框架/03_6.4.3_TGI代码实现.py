"""
HuggingFace TGI（Text Generation Inference）完整示例
展示如何部署和使用TGI进行LLM推理
"""

import os                           # 操作系统接口
import json                         # JSON处理
from typing import List, Dict       # 类型提示

def tgi_docker_deployment():
    """1. TGI Docker部署示例
    
    展示如何使用Docker快速部署TGI服务
    """
    print("=" * 60)
    print("TGI Docker部署示例")
    print("=" * 60)
    
    # Docker部署命令
    docker_command = """
# 使用Docker部署TGI服务
# --model-id: 指定HuggingFace模型
# --port: 服务端口
# --quantize: 量化方式（可选：bitsandbytes, gptq, awq）

docker run --gpus all \\
    --shm-size 1g \\
    -p 8080:80 \\
    -v $PWD/data:/data \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id Qwen/Qwen2.5-0.5B-Instruct \\
    --port 80

# 带量化部署（减少显存占用）
docker run --gpus all \\
    --shm-size 1g \\
    -p 8080:80 \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id meta-llama/Llama-3.1-8B-Instruct \\
    --quantize bitsandbytes-nf4
"""
    print(docker_command)
    
    print("\n✅ 部署命令说明:")
    print("  --gpus all: 使用所有可用GPU")
    print("  --shm-size 1g: 设置共享内存大小")
    print("  --quantize: 启用模型量化")
    print("  --port: 服务监听端口")


def tgi_client_example():
    """2. TGI客户端调用示例
    
    展示如何调用TGI API进行文本生成
    """
    print("\n" + "=" * 60)
    print("TGI客户端调用示例")
    print("=" * 60)
    
    # 使用requests库调用
    requests_example = """
import requests                       # HTTP请求库
import json                          # JSON处理

# TGI服务地址
TGI_URL = "http://localhost:8080"

def tgi_generate(
    prompt: str,
    max_new_tokens: int = 256,
    temperature: float = 0.7,
    top_p: float = 0.9,
    do_sample: bool = True,
) -> str:
    '''3. 调用TGI生成文本
    
    参数:
        prompt: 输入提示词
        max_new_tokens: 最大生成token数
        temperature: 采样温度
        top_p: 核采样参数
        do_sample: 是否使用采样
    返回:
        生成的文本
    '''
    # 4. 构建请求体
    payload = {
        "inputs": prompt,              # 输入文本
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": do_sample,
            "return_full_text": False,  # 只返回生成部分
        }
    }
    
    # 5. 发送POST请求
    response = requests.post(
        f"{TGI_URL}/generate",
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    # 6. 解析响应
    result = response.json()
    return result["generated_text"]


# 使用示例
if __name__ == "__main__":
    prompt = "请解释什么是深度学习："
    output = tgi_generate(prompt, max_new_tokens=128)
    print(f"输入: {prompt}")
    print(f"输出: {output}")
"""
    print(requests_example)
    
    # 流式输出示例
    streaming_example = """
def tgi_stream_generate(prompt: str, max_new_tokens: int = 256):
    '''7. TGI流式生成示例
    
    使用Server-Sent Events(SSE)进行流式输出
    '''
    import sseclient                       # SSE客户端库
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_new_tokens,
            "temperature": 0.7,
        }
    }
    
    # 8. 发送流式请求
    response = requests.post(
        f"{TGI_URL}/generate_stream",
        json=payload,
        stream=True,                       # 启用流式响应
        headers={"Content-Type": "application/json"}
    )
    
    # 9. 创建SSE客户端
    client = sseclient.SSEClient(response)
    
    # 逐token处理
    full_text = ""
    for event in client.events():
        if event.data:
            data = json.loads(event.data)
            if "token" in data:
                token = data["token"]["text"]
                full_text += token
                print(token, end="", flush=True)
    
    return full_text
"""
    print("\n流式输出示例:")
    print(streaming_example)


def tgi_openai_compatible():
    """10. TGI OpenAI兼容API示例"""
    print("\n" + "=" * 60)
    print("TGI OpenAI兼容API示例")
    print("=" * 60)
    
    openai_example = """
import openai                          # OpenAI客户端库

# 配置OpenAI客户端指向TGI服务
client = openai.OpenAI(
    base_url="http://localhost:8080/v1",   # TGI OpenAI兼容端点
    api_key="dummy"                        # TGI不需要API key
)

# 11. 使用Responses API
response = client.chat.completions.create(
    model="tgi",                           # TGI使用"tgi"作为模型名
    messages=[
        {"role": "system", "content": "你是一个有帮助的AI助手。"},
        {"role": "user", "content": "什么是RAG技术？"}
    ],
    max_tokens=256,
    temperature=0.7,
    stream=False,
)

print(response.choices[0].message.content)

# 12. 流式输出
stream = client.chat.completions.create(
    model="tgi",
    messages=[{"role": "user", "content": "讲一个短故事"}],
    max_tokens=128,
    stream=True,
)

for chunk in stream:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
"""
    print(openai_example)


def tgi_quantization_guide():
    """13. TGI量化部署指南"""
    
    print("\n" + "=" * 60)
    print("TGI量化部署指南")
    print("=" * 60)
    
    quantization_guide = """
TGI支持多种量化方式：

1. bitsandbytes (推荐用于消费级GPU)
   --quantize bitsandbytes-nf4    # 4-bit量化
   --quantize bitsandbytes-fp4    # 4-bit浮点量化

2. GPTQ (需要预量化模型)
   --quantize gptq

3. AWQ (需要预量化模型)
   --quantize awq

量化效果对比：

| 量化方式 | 精度 | 显存节省 | 速度 | 精度损失 |
|---------|------|---------|------|---------|
| FP16 | 16bit | 基准 | 基准 | 无 |
| bitsandbytes-nf4 | 4bit | 75% | 1.2x | 小 |
| GPTQ | 4bit | 75% | 1.5x | 小 |
| AWQ | 4bit | 75% | 1.8x | 很小 |

部署示例：

# 4-bit量化部署Llama-3.1-8B（仅需6GB显存）
docker run --gpus all -p 8080:80 \\
    ghcr.io/huggingface/text-generation-inference:latest \\
    --model-id meta-llama/Llama-3.1-8B-Instruct \\
    --quantize bitsandbytes-nf4
"""
    print(quantization_guide)


if __name__ == "__main__":
    tgi_docker_deployment()
    tgi_client_example()
    tgi_openai_compatible()
    tgi_quantization_guide()
