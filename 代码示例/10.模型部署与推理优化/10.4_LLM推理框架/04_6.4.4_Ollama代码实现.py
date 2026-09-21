"""
Ollama完整使用示例
展示如何使用Ollama进行本地LLM部署和推理
"""

import os                           # 操作系统接口
import json                         # JSON处理
import subprocess                   # 子进程管理
from typing import List, Optional   # 类型提示

def ollama_installation_guide():
    """1. Ollama安装指南"""
    print("=" * 60)
    print("Ollama安装指南")
    print("=" * 60)
    
    install_guide = """
1. macOS / Linux 安装:
   curl -fsSL https://ollama.com/install.sh | sh

2. Windows 安装:
   下载安装包: https://ollama.com/download/windows

3. Docker 安装:
   docker pull ollama/ollama
   docker run -d -v ollama:/root/.ollama -p 11434:11434 \\
       --name ollama ollama/ollama

4. 验证安装:
   ollama --version

常用模型:

| 模型 | 参数量 | 显存需求 | 拉取命令 |
|------|--------|---------|---------|
| Llama 3.2 | 1B | ~1GB | ollama pull llama3.2:1b |
| Llama 3.1 | 8B | ~5GB | ollama pull llama3.1 |
| Qwen 2.5 | 7B | ~4GB | ollama pull qwen2.5:7b |
| Mistral | 7B | ~4GB | ollama pull mistral |
| DeepSeek Coder | 6.7B | ~4GB | ollama pull deepseek-coder:6.7b |
"""
    print(install_guide)


def ollama_cli_commands():
    """2. Ollama命令行操作示例"""
    print("\n" + "=" * 60)
    print("Ollama命令行操作")
    print("=" * 60)
    
    commands = """
# 1. 拉取模型
ollama pull llama3.2              # 拉取默认版本
ollama pull llama3.1:70b          # 拉取特定版本

# 2. 查看已安装模型
ollama list

# 3. 运行交互式对话
ollama run llama3.2

# 4. 单次推理
ollama run llama3.2 "请解释什么是机器学习"

# 5. 从文件读取提示词
ollama run llama3.2 < prompt.txt

# 6. 查看模型信息
ollama show llama3.2

# 7. 删除模型
ollama rm llama3.2

# 8. 创建自定义模型
# 创建 Modelfile:
# FROM llama3.2
# PARAMETER temperature 0.7
# SYSTEM 你是一个专业的Python编程助手。

ollama create my-python-assistant -f Modelfile

# 9. 推送模型到仓库
ollama push my-username/my-model

# 10. 复制模型
ollama cp llama3.2 my-llama
"""
    print(commands)


def ollama_python_sdk():
    """3. Ollama Python SDK使用示例"""
    print("\n" + "=" * 60)
    print("Ollama Python SDK示例")
    print("=" * 60)
    
    sdk_example = """
# 安装SDK: pip install ollama

import ollama                         # 4. Ollama官方Python SDK

def basic_chat():
    '''5. 基础对话示例'''
    # 简单对话
    response = ollama.chat(
        model='llama3.2',              # 模型名称
        messages=[
            {'role': 'user', 'content': '什么是深度学习？'}
        ]
    )
    print(response['message']['content'])


def streaming_chat():
    '''6. 流式对话示例'''
    # 流式输出，逐token返回
    stream = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': '写一首关于春天的诗'}],
        stream=True,                   # 启用流式输出
    )
    
    print("流式输出: ")
    for chunk in stream:
        print(chunk['message']['content'], end='', flush=True)
    print()


def multi_turn_conversation():
    '''7. 多轮对话示例'''
    messages = []
    
    while True:
        user_input = input("你: ")
        if user_input.lower() in ['exit', 'quit', 'q']:
            break
        
        # 添加用户消息到历史
        messages.append({'role': 'user', 'content': user_input})
        
        # 获取模型回复
        response = ollama.chat(
            model='llama3.2',
            messages=messages
        )
        
        assistant_reply = response['message']['content']
        print(f"助手: {assistant_reply}")
        
        # 添加助手回复到历史
        messages.append({'role': 'assistant', 'content': assistant_reply})


def generate_text():
    '''8. 文本生成示例（非对话模式）'''
    response = ollama.generate(
        model='llama3.2',
        prompt='请写一篇关于AI的短文',
        # 可选参数
        options={
            'temperature': 0.7,        # 温度
            'top_p': 0.9,              # 核采样
            'top_k': 40,               # Top-K
            'num_predict': 256,        # 最大生成token数
        }
    )
    print(response['response'])


def embedding_example():
    '''9. 生成文本嵌入向量'''
    response = ollama.embeddings(
        model='llama3.2',
        prompt='这是一段需要嵌入的文本'
    )
    embedding = response['embedding']
    print(f"嵌入向量维度: {len(embedding)}")
    print(f"前10维: {embedding[:10]}")


def batch_generate():
    '''10. 批量生成示例'''
    prompts = [
        "什么是Python？",
        "什么是机器学习？",
        "什么是深度学习？"
    ]
    
    for prompt in prompts:
        response = ollama.generate(model='llama3.2', prompt=prompt)
        print(f"Q: {prompt}")
        print(f"A: {response['response'][:100]}...")
        print()


# 自定义模型参数
def custom_model_params():
    '''11. 自定义模型参数'''
    response = ollama.chat(
        model='llama3.2',
        messages=[{'role': 'user', 'content': '创意写作：一个神奇的世界'}],
        options={
            'temperature': 1.2,        # 更高温度，更有创意
            'top_p': 0.95,
            'seed': 42,                # 固定随机种子
        }
    )
    print(response['message']['content'])


if __name__ == "__main__":
    basic_chat()
"""
    print(sdk_example)


def ollama_api_example():
    """12. Ollama REST API调用示例"""
    print("\n" + "=" * 60)
    print("Ollama REST API示例")
    print("=" * 60)
    
    api_example = """
import requests                       # HTTP请求库
import json                          # JSON处理

OLLAMA_URL = "http://localhost:11434"   # Ollama默认地址

def api_generate(prompt: str, model: str = "llama3.2"):
    '''13. 使用REST API生成文本
    
    参数:
        prompt: 输入提示词
        model: 模型名称
    返回:
        生成的文本
    '''
    response = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False            # 非流式输出
        }
    )
    result = response.json()
    return result["response"]


def api_chat(messages: list, model: str = "llama3.2"):
    '''14. 使用REST API进行对话
    
    参数:
        messages: 消息列表 [{"role": "user", "content": "..."}]
        model: 模型名称
    返回:
        助手回复
    '''
    response = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False
        }
    )
    result = response.json()
    return result["message"]["content"]


def api_embeddings(text: str, model: str = "llama3.2"):
    '''15. 使用REST API生成嵌入向量
    
    参数:
        text: 输入文本
        model: 模型名称
    返回:
        嵌入向量列表
    '''
    response = requests.post(
        f"{OLLAMA_URL}/api/embeddings",
        json={
            "model": model,
            "prompt": text
        }
    )
    result = response.json()
    return result["embedding"]


def api_list_models():
    '''16. 列出所有本地模型'''
    response = requests.get(f"{OLLAMA_URL}/api/tags")
    models = response.json()["models"]
    
    print("本地模型列表:")
    for model in models:
        print(f"  - {model['name']}: {model['size'] / 1e9:.2f} GB")


# OpenAI兼容API
def openai_compatible_chat():
    '''17. Ollama提供OpenAI兼容API
    可以直接使用OpenAI SDK
    '''
    import openai
    
    client = openai.OpenAI(
        base_url="http://localhost:11434/v1",  # Ollama OpenAI兼容端点
        api_key="ollama"                        # 任意值
    )
    
    response = client.chat.completions.create(
        model="llama3.2",
        messages=[
            {"role": "system", "content": "你是一个有帮助的助手"},
            {"role": "user", "content": "你好！"}
        ]
    )
    
    print(response.choices[0].message.content)


if __name__ == "__main__":
    # 测试生成
    result = api_generate("什么是机器学习？")
    print(f"生成结果: {result[:200]}...")
    
    # 列出模型
    api_list_models()
"""
    print(api_example)


def ollama_custom_model():
    """18. Ollama自定义模型示例"""
    print("\n" + "=" * 60)
    print("Ollama自定义模型")
    print("=" * 60)
    
    custom_model_guide = """
创建自定义模型（Modelfile）:

1. 创建 Modelfile 文件:

# 基础模型
FROM llama3.2

# 设置系统提示词
SYSTEM 你是一个专业的Python编程专家，擅长解释代码和提供最佳实践。

# 设置参数
PARAMETER temperature 0.7
PARAMETER top_p 0.9
PARAMETER top_k 40

# 设置停止词
PARAMETER stop "<|endoftext|>"
PARAMETER stop "```"

2. 创建模型:
   ollama create my-python-expert -f Modelfile

3. 运行自定义模型:
   ollama run my-python-expert
"""
    print(custom_model_guide)


def ollama_comparison_table():
    """19. LLM推理框架综合对比"""
    print("\n" + "=" * 60)
    print("LLM推理框架综合对比")
    print("=" * 60)
    
    comparison = """
+------------------+--------+--------+-------+-----------+
| 特性             | vLLM   | TRT-LLM| TGI   | Ollama    |
+------------------+--------+--------+-------+-----------+
| **易用性**       | ★★★   | ★★     | ★★★  | ★★★★★    |
| **性能**         | ★★★★  | ★★★★★ | ★★★★ | ★★★      |
| **显存效率**     | ★★★★  | ★★★★  | ★★★  | ★★★      |
| **API兼容**      | OpenAI | 自定义 | OpenAI| OpenAI    |
| **量化支持**     | 多种   | 多种   | 多种  | 自动      |
| **多GPU**        | 支持   | 支持   | 支持  | 单GPU     |
| **部署难度**     | 中     | 高     | 中    | 极低      |
| **生产就绪**     | 是     | 是     | 是    | 开发      |
+------------------+--------+--------+-------+-----------+

选择建议:

| 场景 | 推荐框架 | 原因 |
|------|---------|------|
| 本地开发/测试 | Ollama | 最简单，一行命令 |
| 生产服务（低成本）| vLLM | 开源，高性能，易部署 |
| 生产服务（极致性能）| TensorRT-LLM | NVIDIA优化，最高性能 |
| HuggingFace生态 | TGI | 官方支持，无缝集成 |
| 消费级GPU | Ollama/vLLM | 显存效率高 |
| 企业级部署 | TensorRT-LLM | 稳定性和性能保证 |
"""
    print(comparison)


if __name__ == "__main__":
    ollama_installation_guide()
    ollama_cli_commands()
    ollama_python_sdk()
    ollama_api_example()
    ollama_custom_model()
    ollama_comparison_table()
