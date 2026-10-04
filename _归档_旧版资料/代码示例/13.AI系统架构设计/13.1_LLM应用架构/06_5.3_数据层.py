# 数据层示例
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import json

class ConversationStorage(ABC):
    """对话存储抽象接口"""
    
    @abstractmethod
    def save_message(self, session_id: str, role: str, content: str):
        """保存消息"""
        pass
    
    @abstractmethod
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取历史消息"""
        pass
    
    @abstractmethod
    def delete_session(self, session_id: str):
        """删除会话"""
        pass


class FileConversationStorage(ConversationStorage):
    """文件存储实现"""
    
    def __init__(self, storage_dir: str = "./data/conversations"):
        import os
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
    def _get_file_path(self, session_id: str) -> str:
        import os
        return os.path.join(self.storage_dir, f"{session_id}.json")
    
    def save_message(self, session_id: str, role: str, content: str):
        """保存消息到文件"""
        file_path = self._get_file_path(session_id)
        
        # 读取现有数据
        messages = []
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        
        # 添加新消息
        messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        
        # 写回文件
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
    
    def get_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """从文件读取历史"""
        import os
        file_path = self._get_file_path(session_id)
        
        if not os.path.exists(file_path):
            return []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            messages = json.load(f)
        
        return messages[-limit:]
    
    def delete_session(self, session_id: str):
        """删除会话文件"""
        import os
        file_path = self._get_file_path(session_id)
        if os.path.exists(file_path):
            os.remove(file_path)


class VectorStorage:
    """向量存储层"""
    
    def __init__(self, provider: str = "faiss", **kwargs):
        self.provider = provider
        self.config = kwargs
        
        if provider == "faiss":
            import faiss
            import numpy as np
            self.dimension = kwargs.get("dimension", 768)
            self.index = faiss.IndexFlatL2(self.dimension)
            self.documents = []
            
        elif provider == "qdrant":
            from qdrant_client import QdrantClient
            self.client = QdrantClient(**kwargs)
            
        elif provider == "milvus":
            from pymilvus import connections, Collection
            connections.connect(**kwargs)
            
    def add(self, documents: List[Dict]):
        """添加文档"""
        if self.provider == "faiss":
            import numpy as np
            for doc in documents:
                # 简化：生成随机向量
                vector = np.random.random(self.dimension).astype('float32')
                self.index.add(vector.reshape(1, -1))
                self.documents.append(doc)
    
    def search(self, query_vector, k: int = 10) -> List[Dict]:
        """搜索"""
        if self.provider == "faiss":
            import numpy as np
            distances, indices = self.index.search(
                query_vector.reshape(1, -1), k
            )
            results = []
            for i, idx in enumerate(indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    results.append({
                        "document": self.documents[idx],
                        "distance": float(distances[0][i])
                    })
            return results
        return []
