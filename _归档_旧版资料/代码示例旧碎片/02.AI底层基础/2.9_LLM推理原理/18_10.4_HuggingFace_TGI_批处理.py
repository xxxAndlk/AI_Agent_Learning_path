"""
HuggingFace Text Generation Inference (TGI) 批处理
TGI也支持连续批处理和优化的推理
"""

# 使用TGI的Python客户端
from text_generation import Client

# 连接TGI服务
client = Client("http://localhost:8080")

# 批量请求
prompts = [
    "什么是机器学习？",
    "解释深度学习：",
    "神经网络的基本原理？",
]

# 生成（自动批处理）
for prompt in prompts:
    response = client.generate(
        prompt,
        max_new_tokens=100,
        temperature=0.7,
    )
    print(f"响应: {response.generated_text}")

# 或者使用异步批量API
import asyncio

async def batch_generate():
    """异步批量生成"""
    tasks = [
        client.generate_async(prompt, max_new_tokens=100)
        for prompt in prompts
    ]
    responses = await asyncio.gather(*tasks)
    return responses

# 使用transformers的DataLoader进行批处理
from torch.utils.data import DataLoader
from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")

def collate_fn(batch):
    """批处理数据整理"""
    return tokenizer(
        batch,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=2048,
    )

# 创建DataLoader
prompts_dataset = [...]  # 你的提示列表
dataloader = DataLoader(
    prompts_dataset,
    batch_size=8,
    collate_fn=collate_fn,
)

# 批量推理
for batch in dataloader:
    outputs = model.generate(
        **batch,
        max_new_tokens=100,
    )
    # 处理输出...
