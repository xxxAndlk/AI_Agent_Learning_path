# 业务层示例
from typing import List, Dict, Optional

class BusinessLayer:
    """业务层"""
    
    def __init__(
        self,
        llm_service,
        vector_store,
        cache_service,
        prompt_manager
    ):
        self.llm_service = llm_service
        self.vector_store = vector_store
        self.cache_service = cache_service
        self.prompt_manager = prompt_manager
        
    def process_message(
        self,
        user_id: str,
        message: str,
        session_id: str
    ) -> Dict:
        """处理消息"""
        
        # 1. 获取对话历史
        history = self._get_conversation_history(session_id)
        
        # 2. RAG检索（如启用）
        context = self._retrieve_context(message)
        
        # 3. 构建提示词
        prompt = self.prompt_manager.build_prompt(
            user_message=message,
            history=history,
            context=context
        )
        
        # 4. 调用LLM
        response = self.llm_service.generate(prompt)
        
        # 5. 保存对话历史
        self._save_conversation(session_id, user_id, message, response)
        
        return {
            "response": response,
            "usage": {"prompt_tokens": 100, "completion_tokens": 50}
        }
    
    def _get_conversation_history(self, session_id: str) -> List[Dict]:
        """获取对话历史"""
        # 从存储获取对话历史
        return []
    
    def _retrieve_context(self, query: str) -> str:
        """检索上下文"""
        if not self.vector_store:
            return ""
        
        docs = self.vector_store.similarity_search(query, k=3)
        return "\n\n".join([doc["content"] for doc in docs])
    
    def _save_conversation(self, session_id: str, user_id: str, 
                          user_msg: str, assistant_msg: str):
        """保存对话"""
        # 保存到存储
        pass
