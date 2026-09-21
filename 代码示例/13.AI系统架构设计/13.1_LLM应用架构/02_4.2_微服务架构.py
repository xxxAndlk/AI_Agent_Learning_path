# 微服务架构示例
from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import requests
import json

# ============ 服务接口定义 ============

class LLMServiceInterface(ABC):
    """LLM服务接口"""
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """生成响应"""
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, callback, **kwargs):
        """流式生成"""
        pass


class VectorStoreInterface(ABC):
    """向量存储接口"""
    
    @abstractmethod
    def add_documents(self, documents: List[Dict]):
        """添加文档"""
        pass
    
    @abstractmethod
    def similarity_search(self, query: str, k: int) -> List[Dict]:
        """相似度搜索"""
        pass


class CacheServiceInterface(ABC):
    """缓存服务接口"""
    
    @abstractmethod
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        pass
    
    @abstractmethod
    def set(self, key: str, value: str, ttl: int = 3600):
        """设置缓存"""
        pass


# ============ 微服务实现 ============

class OpenAILLMService(LLMServiceInterface):
    """OpenAI LLM服务（远程服务客户端）"""
    
    def __init__(self, api_key: str, base_url: str = "https://api.openai.com/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = "gpt-5.4-mini"
        
    def generate(self, prompt: str, **kwargs) -> str:
        """调用OpenAI API生成响应"""
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        
        model = kwargs.get("model", self.default_model)
        temperature = kwargs.get("temperature", 0.7)
        max_tokens = kwargs.get("max_tokens", 2000)
        
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        return response.choices[0].message.content
    
    def stream_generate(self, prompt: str, callback, **kwargs):
        """流式生成"""
        import openai
        client = openai.OpenAI(api_key=self.api_key)
        
        model = kwargs.get("model", self.default_model)
        
        stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            stream=True
        )
        
        full_response = ""
        for chunk in stream:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                callback(content)
        
        return full_response


class QdrantVectorService(VectorStoreInterface):
    """Qdrant向量存储服务客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 6333):
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        
    def add_documents(self, documents: List[Dict]):
        """添加文档到向量存储"""
        # 实际实现会调用Qdrant API
        pass
    
    def similarity_search(self, query: str, k: int) -> List[Dict]:
        """相似度搜索"""
        # 实际实现会调用Qdrant API
        # 这里返回模拟数据
        return [{"content": "相关文档内容", "score": 0.95}]


class RedisCacheService(CacheServiceInterface):
    """Redis缓存服务客户端"""
    
    def __init__(self, host: str = "localhost", port: int = 6379):
        import redis
        self.client = redis.Redis(host=host, port=port, decode_responses=True)
        
    def get(self, key: str) -> Optional[str]:
        """获取缓存"""
        return self.client.get(key)
    
    def set(self, key: str, value: str, ttl: int = 3600):
        """设置缓存"""
        self.client.setex(key, ttl, value)


# ============ 服务编排层 ============

class LLMServiceOrchestrator:
    """LLM服务编排器"""
    
    def __init__(
        self,
        llm_service: LLMServiceInterface,
        vector_service: Optional[VectorStoreInterface] = None,
        cache_service: Optional[CacheServiceInterface] = None
    ):
        self.llm_service = llm_service
        self.vector_service = vector_service
        self.cache_service = cache_service
        
    def chat(self, message: str, use_rag: bool = True, 
             use_cache: bool = True) -> str:
        """处理聊天请求"""
        
        # 1. 检查缓存
        if use_cache and self.cache_service:
            cached = self.cache_service.get(f"chat:{hash(message)}")
            if cached:
                return cached
        
        # 2. RAG检索
        context = ""
        if use_rag and self.vector_service:
            docs = self.vector_service.similarity_search(message, k=3)
            context = "\n\n".join([d["content"] for d in docs])
        
        # 3. 构建提示词
        if context:
            prompt = f"基于以下上下文回答问题。\n\n上下文：\n{context}\n\n问题：{message}\n\n回答："
        else:
            prompt = message
        
        # 4. 调用LLM服务
        response = self.llm_service.generate(prompt)
        
        # 5. 写入缓存
        if use_cache and self.cache_service:
            self.cache_service.set(f"chat:{hash(message)}", response)
        
        return response
    
    def stream_chat(self, message: str, callback):
        """流式聊天"""
        response = self.llm_service.stream_generate(
            message,
            callback=callback
        )
        return response
