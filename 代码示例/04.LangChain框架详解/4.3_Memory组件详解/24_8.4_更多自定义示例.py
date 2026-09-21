from langchain_core.memory import BaseMemory
from langchain_core.messages import HumanMessage, AIMessage
from typing import Any, Dict, List

class PreferenceMemory(BaseMemory):
    """
    只记住用户偏好的内存
    自动过滤和提取偏好信息
    """
    
    def __init__(self):
        self.preferences: Dict[str, Any] = {}
    
    @property
    def memory_variables(self) -> List[str]:
        return ["user_preferences"]
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return {"user_preferences": self.preferences}
    
    def save_context(self, inputs: Dict[str, Any], output: str | Any) -> None:
        """从对话中提取并保存偏好"""
        user_input = inputs.get("input", "")
        
        # 简单的偏好提取逻辑
        preference_keywords = {
            "喜欢": "likes",
            "讨厌": "dislikes",
            "想要": "wants",
            "需要": "needs"
        }
        
        for keyword, key in preference_keywords.items():
            if keyword in user_input:
                # 简化处理：提取关键词后面的内容
                parts = user_input.split(keyword)
                if len(parts) > 1:
                    value = parts[1].strip("，。！？")
                    if key not in self.preferences:
                        self.preferences[key] = []
                    if value not in self.preferences[key]:
                        self.preferences[key].append(value)
    
    def clear(self) -> None:
        self.preferences = {}


class SlidingWindowSummaryMemory(BaseMemory):
    """
    滑动窗口+摘要混合内存
    窗口内保持原始对话，窗口外自动摘要
    """
    
    def __init__(self, llm, window_size: int = 4, max_summary_tokens: int = 500):
        from langchain.memory import ConversationSummaryBufferMemory
        self._memory = ConversationSummaryBufferMemory(
            llm=llm,
            memory_key="history",
            return_messages=True,
            max_token_limit=max_summary_tokens
        )
        self.window_size = window_size
    
    @property
    def memory_variables(self) -> List[str]:
        return self._memory.memory_variables
    
    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        return self._memory.load_memory_variables(inputs)
    
    def save_context(self, inputs: Dict[str, Any], output: str | Any) -> None:
        self._memory.save_context(inputs, output)
    
    def clear(self) -> None:
        self._memory.clear()
