"""
WebSocket流式生成实现
适合需要双向通信的场景
"""

import asyncio
import websockets
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# WebSocket服务器
async def llm_websocket(websocket, path):
    """LLM WebSocket处理"""
    
    # 加载模型（启动时加载一次）
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf",
        torch_dtype=torch.float16,
        device_map="auto",
    )
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    
    try:
        async for message in websocket:
            data = json.loads(message)
            prompt = data.get("prompt", "")
            max_tokens = data.get("max_tokens", 200)
            
            # 编码
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
            generated = input_ids
            
            # 流式生成
            for _ in range(max_tokens):
                with torch.no_grad():
                    outputs = model(generated)
                    next_token = torch.argmax(outputs.logits[:, -1, :])
                    
                    if next_token.item() == tokenizer.eos_token_id:
                        break
                
                generated = torch.cat([generated, next_token.unsqueeze(0)])
                token_text = tokenizer.decode(next_token)
                
                # 发送token
                await websocket.send(json.dumps({
                    "type": "token",
                    "content": token_text,
                }))
            
            # 完成
            await websocket.send(json.dumps({"type": "done"}))
    
    except Exception as e:
        await websocket.send(json.dumps({
            "type": "error",
            "message": str(e),
        }))

# 启动服务
# async with websockets.serve(llm_websocket, "localhost", 8765):
#     await asyncio.Future()
