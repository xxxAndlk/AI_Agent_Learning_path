"""
Server-Sent Events (SSE) 流式生成实现
"""

import json
import sse
from typing import Generator
from flask import Flask, Response, request
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = Flask(__name__)

# 加载模型
model = None
tokenizer = None

def get_model():
    """延迟加载模型"""
    global model, tokenizer
    if model is None:
        model = AutoModelForCausalLM.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf",
            torch_dtype=torch.float16,
            device_map="auto",
        )
        tokenizer = AutoTokenizer.from_pretrained(
            "meta-llama/Llama-2-7b-chat-hf"
        )
    return model, tokenizer

def stream_generate(prompt: str, max_new_tokens: int = 200) -> Generator[str, None, None]:
    """流式生成器"""
    model, tokenizer = get_model()
    
    # 编码输入
    input_ids = tokenizer.encode(prompt, return_tensors="pt").to(model.device)
    
    # 逐token生成
    generated = input_ids
    generated_text = ""
    
    for _ in range(max_new_tokens):
        with torch.no_grad():
            outputs = model(generated)
            logits = outputs.logits[:, -1, :]
            
            # 贪婪采样（可改为其他采样策略）
            next_token = torch.argmax(logits, dim=-1, keepdim=True)
            
            # 检查结束
            if next_token.item() == tokenizer.eos_token_id:
                break
        
        generated = torch.cat([generated, next_token], dim=1)
        token_text = tokenizer.decode(next_token[0], skip_special_tokens=True)
        generated_text += token_text
        
        # SSE格式发送
        yield f"data: {json.dumps({'token': token_text, 'text': generated_text})}\n\n"
    
    # 结束信号
    yield f"data: {json.dumps({'done': True})}\n\n"

@app.route("/stream_generate", methods=["POST"])
def stream_generate_api():
    """SSE流式生成API"""
    data = request.json
    prompt = data.get("prompt", "")
    max_new_tokens = data.get("max_new_tokens", 200)
    
    return Response(
        stream_generate(prompt, max_new_tokens),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # 禁用Nginx缓冲
        },
    )

# 前端JavaScript示例
frontend_js = """
// 前端使用EventSource接收流式输出
const eventSource = new EventSource('/stream_generate', {
    method: 'POST',
    body: JSON.stringify({prompt: '写一个故事：'}),
    headers: {'Content-Type': 'application/json'}
});

eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    if (data.done) {
        console.log('生成完成');
        eventSource.close();
    } else {
        // 追加新token到UI
        document.getElementById('output').textContent += data.token;
    }
};

eventSource.onerror = (error) => {
    console.error('SSE错误:', error);
    eventSource.close();
};
"""
