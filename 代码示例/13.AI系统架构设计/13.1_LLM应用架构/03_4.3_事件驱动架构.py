import asyncio
from typing import Callable, Dict, List
from dataclasses import dataclass
from datetime import datetime
import json

# ============ 事件定义 ============

@dataclass
class ChatEvent:
    """聊天事件"""
    event_id: str
    user_id: str
    message: str
    timestamp: datetime
    metadata: Dict = None

@dataclass
class LLMRequestEvent:
    """LLM请求事件"""
    request_id: str
    prompt: str
    model: str
    temperature: float
    callback: Callable = None

@dataclass
class LLMResponseEvent:
    """LLM响应事件"""
    request_id: str
    response: str
    token_usage: Dict
    latency_ms: float

@dataclass
class CacheEvent:
    """缓存事件"""
    key: str
    value: str
    action: str  # 'set' or 'delete'

# ============ 事件总线 ============

class EventBus:
    """事件总线"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        
    def subscribe(self, event_type: str, handler: Callable):
        """订阅事件"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        
    def publish(self, event_type: str, event: any):
        """发布事件"""
        if event_type in self.subscribers:
            for handler in self.subscribers[event_type]:
                handler(event)
                
    async def publish_async(self, event_type: str, event: any):
        """异步发布事件"""
        if event_type in self.subscribers:
            tasks = []
            for handler in self.subscribers[event_type]:
                if asyncio.iscoroutinefunction(handler):
                    tasks.append(handler(event))
                else:
                    handler(event)
            if tasks:
                await asyncio.gather(*tasks)


# ============ 事件处理器 ============

class LLMEventHandler:
    """LLM事件处理器"""
    
    def __init__(self, llm_service, event_bus: EventBus):
        self.llm_service = llm_service
        self.event_bus = event_bus
        self.pending_requests: Dict[str, asyncio.Future] = {}
        
        # 订阅响应事件
        self.event_bus.subscribe("llm_response", self.handle_response)
        
    async def handle_request(self, event: LLMRequestEvent) -> str:
        """处理LLM请求事件"""
        start_time = datetime.now()
        
        # 创建Future用于异步返回
        future = asyncio.Future()
        self.pending_requests[event.request_id] = future
        
        # 实际调用LLM（这里简化处理）
        try:
            response = self.llm_service.generate(
                event.prompt,
                model=event.model,
                temperature=event.temperature
            )
            
            latency = (datetime.now() - start_time).total_seconds() * 1000
            
            # 发布响应事件
            response_event = LLMResponseEvent(
                request_id=event.request_id,
                response=response,
                token_usage={"total": len(response)},
                latency_ms=latency
            )
            self.event_bus.publish("llm_response", response_event)
            
            return response
            
        except Exception as e:
            # 发布错误事件
            self.event_bus.publish("llm_error", {
                "request_id": event.request_id,
                "error": str(e)
            })
            raise
            
        finally:
            self.pending_requests.pop(event.request_id, None)
    
    def handle_response(self, event: LLMResponseEvent):
        """处理LLM响应事件"""
        if event.request_id in self.pending_requests:
            future = self.pending_requests[event.request_id]
            if not future.done():
                future.set_result(event.response)


# ============ 异步工作流 ============

class AsyncLLMWorkflow:
    """异步LLM工作流"""
    
    def __init__(self):
        self.event_bus = EventBus()
        self.llm_service = None
        self.vector_service = None
        self.cache_service = None
        
    def initialize(self, config: dict):
        """初始化服务"""
        # 初始化各个服务
        self.llm_service = OpenAILLMService(config["api_key"])
        self.vector_service = QdrantVectorService()
        # 事件处理器
        self.handler = LLMEventHandler(self.llm_service, self.event_bus)
        
    async def process_chat(self, user_id: str, message: str) -> str:
        """异步处理聊天"""
        
        # 1. 检查缓存
        if self.cache_service:
            cached = self.cache_service.get(f"chat:{user_id}:{hash(message)}")
            if cached:
                return cached
        
        # 2. RAG检索
        context = ""
        if self.vector_service:
            docs = self.vector_service.similarity_search(message, k=3)
            context = "\n\n".join([d["content"] for d in docs])
        
        # 3. 构建提示词
        prompt = f"上下文：{context}\n\n问题：{message}" if context else message
        
        # 4. 异步调用LLM
        response = await self.handler.handle_request(
            LLMRequestEvent(
                request_id=f"{user_id}:{datetime.now().timestamp()}",
                prompt=prompt,
                model="gpt-5.4-mini",
                temperature=0.7
            )
        )
        
        # 5. 缓存结果
        if self.cache_service:
            self.cache_service.set(f"chat:{user_id}:{hash(message)}", response)
        
        return response
