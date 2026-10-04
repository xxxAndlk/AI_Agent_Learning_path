import json
from datetime import datetime

class ExportableMemory(ConversationBufferMemory):
    """支持导出导入的Memory"""
    
    def export_state(self) -> dict:
        """导出内存状态"""
        return {
            "exported_at": datetime.now().isoformat(),
            "memory_variables": self.memory_variables,
            "messages": [
                {
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content
                }
                for msg in self.chat_memory.messages
            ]
        }
    
    def import_state(self, state: dict):
        """导入内存状态"""
        self.chat_memory.clear()
        for msg_data in state.get("messages", []):
            if msg_data["type"] == "human":
                self.chat_memory.add_message(HumanMessage(content=msg_data["content"]))
            elif msg_data["type"] == "ai":
                self.chat_memory.add_message(AIMessage(content=msg_data["content"]))
    
    def save_to_file(self, filepath: str):
        """保存到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.export_state(), f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str):
        """从文件加载"""
        with open(filepath, 'r', encoding='utf-8') as f:
            state = json.load(f)
            self.import_state(state)


# 使用示例
memory = ExportableMemory(memory_key="history", return_messages=True)
memory.save_context({"input": "Hello"}, {"text": "Hi there!"})

# 导出
memory.save_to_file("backup.json")

# 导入
new_memory = ExportableMemory(memory_key="history", return_messages=True)
new_memory.load_from_file("backup.json")
print(new_memory.load_memory_variables({}))
