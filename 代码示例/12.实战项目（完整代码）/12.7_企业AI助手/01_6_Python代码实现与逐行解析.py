"""
企业AI助手系统 - 简化版
整合RAG + Agent + MCP的企业级智能助手
提供企业政策查询、会议室预约、邮件发送等功能
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class ChatMessage:
    """聊天消息：定义对话消息的结构
    
    属性:
        role: 消息角色（user/assistant/system）
        content: 消息内容
        timestamp: 消息时间戳
    """
    role: str
    content: str
    timestamp: datetime = None
    
    def __post_init__(self):
        # 初始化时自动设置时间戳
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EnterpriseKnowledgeBase:
    """企业知识库 (RAG)
    
    存储企业内部的政策文档和流程说明
    提供基于关键词的知识检索功能
    """
    
    def __init__(self):
        """初始化知识库：加载预设的企业知识内容"""
        self.documents = {
            "休假政策": "公司员工休假政策：入职满1年享受5天年假...",
            "报销流程": "费用报销流程：准备发票->提交报销单->领导审批...",
            "IT支持": "IT技术支持：联系IT热线4000-1234..."
        }
    
    def search(self, query: str) -> List[Dict]:
        """搜索相关知识
        
        根据用户查询的关键词检索匹配的知识文档
        
        参数:
            query: 用户输入的查询文本
        返回:
            匹配的文档列表，每个元素包含类别和内容
        """
        results = []
        # 遍历知识库，查找包含查询关键词的文档
        for category, content in self.documents.items():
            if any(word in query for word in ["休假", "报销", "IT", "电脑"]):
                results.append({"category": category, "content": content})
        return results


class EnterpriseAIAssistant:
    """企业AI助手
    
    整合知识检索和工具调用的企业级智能助手
    负责处理用户的各类咨询和操作请求
    """
    
    def __init__(self):
        """初始化AI助手：创建知识库和会话存储"""
        self.knowledge_base = EnterpriseKnowledgeBase()
        self.sessions: Dict[str, List[ChatMessage]] = {}
    
    def chat(self, user_input: str, session_id: str = "default") -> Dict:
        """主对话接口：处理用户输入并生成回复
        
        参数:
            user_input: 用户输入的文本
            session_id: 会话ID，用于标识不同的用户会话
        返回:
            包含回复内容、知识使用标记和会话ID的字典
        """
        # 检索知识
        knowledge_results = self.knowledge_base.search(user_input)
        
        # 生成回复：根据不同意图类型生成对应回复
        if knowledge_results:
            # 如果检索到知识库内容，返回相关政策信息
            response = f"根据公司{knowledge_results[0]['category']}，{knowledge_results[0]['content'][:50]}..."
        elif "会议" in user_input:
            # 会议预约意图：模拟预约会议室
            response = "已为您预约会议室A101，时间：明天下午2点"
        elif "邮件" in user_input:
            # 邮件发送意图：模拟发送邮件
            response = "邮件已发送给收件人"
        else:
            # 默认回复：介绍助手能力
            response = "我是您的企业助手，可以帮您查询公司政策、预约会议、发送邮件等。"
        
        return {
            "response": response,
            "knowledge_used": len(knowledge_results) > 0,
            "session_id": session_id
        }


if __name__ == "__main__":
    # 创建AI助手实例
    assistant = EnterpriseAIAssistant()
    
    # 测试查询列表
    test_queries = [
        "请问公司年假政策是什么？",
        "帮我预约明天的会议室",
        "报销流程是怎样的？"
    ]
    
    # 逐个处理测试查询
    for query in test_queries:
        print(f"\n用户: {query}")
        result = assistant.chat(query)
        print(f"助手: {result['response']}")
