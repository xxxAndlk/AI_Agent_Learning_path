import json
from datetime import datetime
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage

class PersistentConversationBufferMemory(ConversationBufferMemory):
    """带文件持久化的Memory"""
    
    def __init__(self, file_path: str = "conversation.json", **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self._load_from_file()
    
    def _load_from_file(self):
        """从文件加载"""
        import os
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 恢复消息
                    for msg in data.get("messages", []):
                        if msg["type"] == "human":
                            self.chat_memory.add_message(HumanMessage(content=msg["content"]))
                        elif msg["type"] == "ai":
                            self.chat_memory.add_message(AIMessage(content=msg["content"]))
            except Exception as e:
                print(f"加载失败: {e}")
    
    def _save_to_file(self):
        """保存到文件"""
        messages = []
        for msg in self.chat_memory.messages:
            msg_type = "human" if isinstance(msg, HumanMessage) else "ai"
            messages.append({
                "type": msg_type,
                "content": msg.content
            })
        
        data = {
            "updated_at": datetime.now().isoformat(),
            "messages": messages
        }
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_context(self, inputs: dict, output: str) -> None:
        """重写save_context，在保存后立即持久化"""
        super().save_context(inputs, output)
        self._save_to_file()
    
    def clear(self) -> None:
        """重写clear，清理时也删除文件"""
        super().clear()
        import os
        if os.path.exists(self.file_path):
            os.remove(self.file_path)


# 使用持久化内存
memory = PersistentConversationBufferMemory(
    file_path="my_conversation.json",
    memory_key="history",
    return_messages=True
)
