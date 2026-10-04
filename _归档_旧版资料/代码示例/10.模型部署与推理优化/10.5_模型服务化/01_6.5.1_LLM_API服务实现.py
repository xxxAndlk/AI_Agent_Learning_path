"""
1. LLM API服务实现
使用FastAPI构建高性能模型服务
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks  # 2. FastAPI核心组件
from fastapi.middleware.cors import CORSMiddleware             # 3. CORS跨域支持
from pydantic import BaseModel                                 # 4. 数据验证模型
from typing import List, Optional, Dict, Any                  # 5. 类型提示
import uvicorn                                                 # 6. ASGI服务器
import asyncio                                                 # 7. 异步编程
from datetime import datetime                                  # 8. 时间处理
import time                                                    # 9. 时间戳

# 10. 创建FastAPI应用
app = FastAPI(title="LLM Service", version="1.0.0")

# 11. 配置CORS中间件
# 允许跨域请求，支持前端应用访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],               # 允许所有来源
    allow_credentials=True,            # 允许携带凭证
    allow_methods=["*"],               # 允许所有HTTP方法
    allow_headers=["*"],               # 允许所有请求头
)

# 12. 定义请求模型
class ChatRequest(BaseModel):
    """13. 聊天补全请求模型"""
    model: str = "default"              # 模型名称
    messages: List[Dict[str, str]]      # 对话历史
    temperature: float = 0.7            # 温度参数
    max_tokens: int = 256               # 最大token数
    stream: bool = False                # 是否流式输出

class CompletionRequest(BaseModel):
    """14. 文本补全请求模型"""
    model: str = "default"
    prompt: str
    temperature: float = 0.7
    max_tokens: int = 256

class EmbeddingRequest(BaseModel):
    """15. 嵌入请求模型"""
    model: str = "default"
    input: str

# 16. 定义响应模型
class ChatResponse(BaseModel):
    """17. 聊天补全响应模型"""
    id: str
    model: str
    choices: List[Dict[str, Any]]
    usage: Dict[str, int]
    created: int

# 18. 模拟模型（实际应加载真实模型）
class MockLLM:
    """19. 模拟LLM模型
    
    在实际生产环境中，这里应该加载真实的LLM模型
    可以使用vLLM、Ollama等框架
    """
    
    def __init__(self, name: str):
        """20. 模型初始化"""
        self.name = name
        self.request_count = 0        # 请求计数
        self.total_tokens = 0         # token计数
    
    async def chat(self, messages: List[Dict], **kwargs) -> str:
        """21. 模拟对话
        
        参数:
            messages: 对话历史
            **kwargs: 其他参数
        返回:
            生成的回复文本
        """
        await asyncio.sleep(0.1)      # 模拟推理延迟
        self.request_count += 1
        
        # 22. 提取最后一条用户消息
        last_message = messages[-1]["content"] if messages else ""
        return f"这是模型'{self.name}'对'{last_message[:20]}...'的回复"
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """23. 模拟文本补全"""
        await asyncio.sleep(0.1)
        self.request_count += 1
        return f"补全结果: {prompt[:20]}..."
    
    async def embed(self, text: str) -> List[float]:
        """24. 模拟嵌入向量生成"""
        import random
        return [random.random() for _ in range(384)]

# 25. 模型管理器
class ModelManager:
    """26. 模型管理器
    
    负责模型的注册、获取和列表
    支持多模型管理
    """
    
    def __init__(self):
        self.models: Dict[str, MockLLM] = {}  # 已加载的模型
        self.default_model = "gpt-5.4-mini"   # 默认模型
    
    def register_model(self, name: str, model: MockLLM):
        """27. 注册模型"""
        self.models[name] = model
    
    def get_model(self, name: str) -> Optional[MockLLM]:
        """28. 获取模型
        
        如果指定模型不存在，返回默认模型
        """
        return self.models.get(name) or self.models.get(self.default_model)
    
    def list_models(self) -> List[str]:
        """29. 列出可用模型"""
        return list(self.models.keys())

# 30. 创建全局模型管理器
model_manager = ModelManager()

# 31. 初始化注册模型
model_manager.register_model("gpt-5.4-mini", MockLLM("gpt-5.4-mini"))
model_manager.register_model("gpt-5.4", MockLLM("gpt-5.4"))
model_manager.register_model("text-embedding-3-small", MockLLM("text-embedding-3-small"))

# 32. 定义路由
@app.get("/")
async def root():
    """33. 根路径"""
    return {"message": "LLM Service API", "version": "1.0.0"}

@app.get("/v1/models")
async def list_models():
    """34. 列出可用模型
    
    返回所有已注册的模型列表
    """
    models = [
        {
            "id": model_id,
            "object": "model",
            "created": int(time.time()),
            "owned_by": "organization-owner"
        }
        for model_id in model_manager.list_models()
    ]
    return {"object": "list", "data": models}

@app.post("/v1/chat/completions")
async def chat_completion(request: ChatRequest):
    """35. 聊天补全API
    
    处理聊天补全请求，返回模型生成的回复
    """
    # 36. 获取模型实例
    model = model_manager.get_model(request.model)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {request.model} not found")
    
    try:
        # 37. 调用模型进行推理
        content = await model.chat(request.messages, temperature=request.temperature)
        
        # 38. 构建响应
        response = ChatResponse(
            id=f"chatcmpl-{int(time.time())}",  # 唯一ID
            model=request.model,
            choices=[{
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop"
            }],
            usage={
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30
            },
            created=int(time.time())
        )
        
        return response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/completions")
async def text_completion(request: CompletionRequest):
    """39. 文本补全API"""
    model = model_manager.get_model(request.model)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {request.model} not found")
    
    try:
        content = await model.complete(request.prompt, temperature=request.temperature)
        
        return {
            "id": f"cmpl-{int(time.time())}",
            "object": "text_completion",
            "model": request.model,
            "choices": [{
                "text": content,
                "index": 0,
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": len(request.prompt.split()),
                "completion_tokens": 20,
                "total_tokens": 30
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/embeddings")
async def create_embedding(request: EmbeddingRequest):
    """40. 嵌入API"""
    model = model_manager.get_model(request.model)
    if not model:
        raise HTTPException(status_code=404, detail=f"Model {request.model} not found")
    
    try:
        embedding = await model.embed(request.input)
        
        return {
            "object": "list",
            "data": [{
                "object": "embedding",
                "embedding": embedding,
                "index": 0
            }],
            "model": request.model,
            "usage": {
                "prompt_tokens": len(request.input.split()),
                "total_tokens": len(request.input.split())
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """41. 健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": len(model_manager.models)
    }

@app.get("/metrics")
async def get_metrics():
    """42. 获取服务指标"""
    return {
        "total_requests": sum(m.request_count for m in model_manager.models.values()),
        "active_models": len(model_manager.models),
        "uptime": "running"
    }

# 43. 启动服务
if __name__ == "__main__":
    print("启动LLM API服务...")
    print("API文档: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
