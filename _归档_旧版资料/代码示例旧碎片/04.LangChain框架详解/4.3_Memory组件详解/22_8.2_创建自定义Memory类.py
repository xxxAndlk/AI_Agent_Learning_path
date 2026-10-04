from langchain_core.memory import BaseMemory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from typing import Any, Dict, List
import json
from datetime import datetime

class CustomDatabaseMemory(BaseMemory):
    """
    自定义数据库内存示例
    将对话历史存储到本地JSON文件
    """
    
    def __init__(self, storage_path: str = "conversation.json", max_turns: int = 10):
        self.storage_path = storage_path
        self.max_turns = max_turns
        self._messages: List[BaseMessage] = []
        self._load()
    
    @property
    def memory_variables(self) -> List[str]:
        """返回内存变量名"""
        return ["conversation_history"]
    
    def _load(self):
        """从文件加载历史"""
        import os
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 反序列化为消息对象
                    for msg_data in data.get("messages", []):
                        if msg_data["type"] == "human":
                            self._messages.append(HumanMessage(content=msg_data["content"]))
                        elif msg_data["type"] == "ai":
                            self._messages.append(AIMessage(content=msg_data["content"]))
            except Exception as e:
                print(f"加载历史失败: {e}")
    
    def _save(self):
        """保存到文件"""
        data = {
            "updated_at": datetime.now().isoformat(),
            "messages": [
                {
                    "type": "human" if isinstance(msg, HumanMessage) else "ai",
                    "content": msg.content
                }
                for msg in self._messages
            ]
        }
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """加载内存变量供Chain使用"""
        return {
            "conversation_history": self._messages
        }
    
    def save_context(self, inputs: Dict[str, Any], output: str | BaseMessage) -> None:
        """保存对话上下文"""
        # 获取用户输入
        user_input = inputs.get("input", "")
        if user_input:
            self._messages.append(HumanMessage(content=user_input))
        
        # 获取AI输出
        if isinstance(output, BaseMessage):
            ai_output = output.content
        else:
            ai_output = str(output)
        if ai_output:
            self._messages.append(AIMessage(content=ai_output))
        
        # 超过最大轮数时删除最早的对话
        while len(self._messages) > self.max_turns * 2:
            self._messages.pop(0)
        
        # 保存到文件
        self._save()
    
    def clear(self) -> None:
        """清空内存"""
        self._messages = []
        self._save()
