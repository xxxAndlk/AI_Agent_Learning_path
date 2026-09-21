from langchain.memory.entity import EntityStore, InMemoryEntityStore
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 1. 内存存储（默认，适合小规模）
entity_store_memory = InMemoryEntityStore()

# 2. 向量存储（适合大规模、需要语义检索）
# 需要先创建向量存储
vectorstore = FAISS.from_texts(
    ["初始"],
    embedding=OpenAIEmbeddings(model="text-embedding-3-small")
)

# 自定义实体存储类
class PersistentEntityStore(EntityStore):
    """持久化实体存储示例"""
    
    def __init__(self, storage_file="entities.json"):
        import json
        self.storage_file = storage_file
        self._entities = self._load()
    
    def _load(self):
        import json, os
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save(self):
        import json
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(self._entities, f, ensure_ascii=False, indent=2)
    
    def get(self, entity_name: str, default=None) -> dict:
        return self._entities.get(entity_name, default)
    
    def put(self, entity_name: str, entity_data: dict) -> None:
        self._entities[entity_name] = entity_data
        self._save()
    
    def get_all(self) -> dict:
        return self._entities.copy()
    
    def delete(self, entity_name: str) -> None:
        if entity_name in self._entities:
            del self._entities[entity_name]
            self._save()
    
    def clear(self) -> None:
        self._entities = {}
        self._save()

# 使用自定义存储
custom_entity_store = PersistentEntityStore("my_entities.json")

memory = ConversationEntityMemory(
    llm=ChatOpenAI(model="gpt-5.4-mini"),
    entity_store=custom_entity_store,
    memory_key="history"
)

import os
