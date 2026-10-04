from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI
from typing import Dict

class MultiUserMemoryManager:
    """多用户Memory管理器"""
    
    def __init__(self):
        self.memories: Dict[str, ConversationBufferMemory] = {}
        self.llm = ChatOpenAI(model="gpt-5.4-mini")
    
    def get_memory(self, user_id: str) -> ConversationBufferMemory:
        """获取或创建用户内存"""
        if user_id not in self.memories:
            self.memories[user_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="text",
                input_key="input"
            )
        return self.memories[user_id]
    
    def clear_user(self, user_id: str):
        """清除用户记忆"""
        if user_id in self.memories:
            self.memories[user_id].clear()
            del self.memories[user_id]
    
    def get_user_history(self, user_id: str) -> list:
        """获取用户历史"""
        memory = self.get_memory(user_id)
        return memory.load_memory_variables({})["chat_history"]


# 使用示例
manager = MultiUserMemoryManager()

# 用户A的对话
memory_a = manager.get_memory("user_a")
memory_a.save_context({"input": "我喜欢Python"}, {"text": "Python很棒！"})
memory_a.save_context({"input": "我最擅长什么？"}, {"text": "你说你喜欢Python"})

# 用户B的对话
memory_b = manager.get_memory("user_b")
memory_b.save_context({"input": "我喜欢Java"}, {"text": "Java是企业级开发的首选"})

# 验证隔离
print("用户A历史:", len(manager.get_user_history("user_a")))
print("用户B历史:", len(manager.get_user_history("user_b")))
