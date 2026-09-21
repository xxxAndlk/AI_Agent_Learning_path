from openai import OpenAI
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import tiktoken

client = OpenAI()

@dataclass
class Message:
    """消息类"""
    role: str                    # 角色: user/assistant/system
    content: str                 # 消息内容
    timestamp: datetime = field(default_factory=datetime.now)  # 时间戳
    token_count: int = 0         # token数量


class ConversationManager:
    """对话管理器
    
    负责多轮对话的上下文管理
    """
    
    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-5.4-mini",
        max_tokens: int = 4000,
        system_prompt: Optional[str] = None
    ):
        """
        初始化对话管理器
        
        Args:
            client: OpenAI客户端
            model: 使用的模型
            max_tokens: 最大token数
            system_prompt: 系统提示
        """
        self.client = client
        self.model = model
        self.max_tokens = max_tokens
        self.system_prompt = system_prompt or "你是一个有帮助的AI助手。"
        
        self.messages: List[Message] = []
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
        # 添加系统消息
        self.add_message("system", self.system_prompt)
    
    def add_message(self, role: str, content: str) -> None:
        """添加消息到对话历史
        
        Args:
            role: 消息角色
            content: 消息内容
        """
        token_count = len(self.tokenizer.encode(content))
        message = Message(
            role=role,
            content=content,
            token_count=token_count
        )
        self.messages.append(message)
    
    def get_total_tokens(self) -> int:
        """获取当前总token数"""
        return sum(m.token_count for m in self.messages)
    
    def trim_to_limit(self, preserve_system: bool = True) -> None:
        """裁剪消息以适应token限制
        
        使用滑动窗口策略，保留最新的消息
        """
        while self.get_total_tokens() > self.max_tokens and len(self.messages) > 1:
            # 总是保留系统消息（如果需要）
            start_idx = 1 if preserve_system and self.messages[0].role == "system" else 0
            
            # 移除最早的非系统消息
            if start_idx < len(self.messages):
                self.messages.pop(start_idx)
    
    def summarize_old_messages(
        self, 
        threshold_tokens: int = 2000
    ) -> None:
        """摘要旧消息
        
        将早期消息压缩为摘要
        
        Args:
            threshold_tokens: 触发摘要的token阈值
        """
        if len(self.messages) < 4:  # 至少需要一些消息才摘要
            return
        
        current_tokens = self.get_total_tokens()
        if current_tokens < threshold_tokens:
            return
        
        # 获取非系统消息（排除最新的1-2条）
        historical = self.messages[1:-2]
        if not historical:
            return
        
        # 构建摘要请求
        history_text = "\n".join([
            f"{m.role}: {m.content}" for m in historical
        ])
        
        summary_prompt = f"""请将以下对话历史压缩成简短的摘要，保留关键信息：

{history_text}

摘要格式：[人物]做了什么事，说了什么话。简洁明了，不超过100字。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.3
        )
        
        summary = response.choices[0].message.content.strip()
        
        # 移除旧消息，添加摘要
        self.messages = [
            self.messages[0],  # 系统消息
            Message(role="system", content=f"之前对话摘要: {summary}"),
            self.messages[-2:]  # 保留最近两条
        ]
    
    def get_relevant_context(
        self, 
        current_query: str,
        top_k: int = 3
    ) -> List[Message]:
        """获取与当前查询相关的上下文
        
        基于语义相似度选择相关历史消息
        
        Args:
            current_query: 当前查询
            top_k: 选择相关消息数量
            
        Returns:
            相关的消息列表
        """
        if len(self.messages) <= 2:
            return self.messages
        
        # 获取历史消息（排除系统消息和最近的消息）
        historical = self.messages[1:-1]
        if not historical:
            return self.messages
        
        # 简单实现：基于关键词重叠
        # 实际应用中可使用embedding相似度
        query_words = set(current_query.lower().split())
        
        relevant = []
        for msg in historical:
            msg_words = set(msg.content.lower().split())
            overlap = len(query_words & msg_words)
            if overlap > 0:
                relevant.append((msg, overlap))
        
        # 按相关性排序，选择top_k
        relevant.sort(key=lambda x: x[1], reverse=True)
        top_messages = [msg for msg, _ in relevant[:top_k]]
        
        # 构建返回的上下文
        if self.messages[0].role == "system":
            return [self.messages[0]] + top_messages + self.messages[-1:]
        return top_messages + self.messages[-1:]
    
    def build_messages(self) -> List[Dict[str, str]]:
        """构建API调用的消息格式
        
        Returns:
            符合OpenAI API格式的消息列表
        """
        return [
            {"role": m.role, "content": m.content}
            for m in self.messages
        ]
    
    def clear(self) -> None:
        """清空对话历史，保留系统消息"""
        system_msg = self.messages[0] if self.messages else None
        self.messages = []
        if system_msg:
            self.messages.append(system_msg)


class ContextWindowManager:
    """上下文窗口管理器
    
    实现更精细的上下文管理策略
    """
    
    def __init__(
        self,
        client: OpenAI,
        model: str = "gpt-5.4-mini",
        max_context_tokens: int = 4000,
        reserved_tokens: int = 500
    ):
        self.client = client
        self.model = model
        self.max_context_tokens = max_context_tokens
        self.reserved_tokens = reserved_tokens
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def estimate_tokens(self, text: str) -> int:
        """估算文本的token数"""
        return len(self.tokenizer.encode(text))
    
    def smart_truncate(
        self,
        messages: List[Dict[str, str]],
        new_message: str
    ) -> List[Dict[str, str]]:
        """智能截断
        
        根据消息重要性进行选择性保留
        
        Args:
            messages: 历史消息
            new_message: 新消息
            
        Returns:
            处理后的消息列表
        """
        available_tokens = self.max_context_tokens - self.reserved_tokens
        
        # 估算新消息的token
        new_tokens = self.estimate_tokens(new_message)
        available_tokens -= new_tokens
        
        if available_tokens <= 0:
            return []
        
        # 估算现有消息
        current_tokens = sum(
            self.estimate_tokens(m["content"]) 
            for m in messages
        )
        
        if current_tokens <= available_tokens:
            return messages
        
        # 需要截断，优先保留最近的
        truncated = []
        total = 0
        
        for msg in reversed(messages):
            msg_tokens = self.estimate_tokens(msg["content"])
            if total + msg_tokens <= available_tokens:
                truncated.insert(0, msg)
                total += msg_tokens
            else:
                break
        
        # 尝试保留至少一条系统消息和用户消息
        return truncated
    
    def compress_messages(
        self,
        messages: List[Dict[str, str]],
        strategy: str = "last"
    ) -> List[Dict[str, str]]:
        """压缩消息列表
        
        Args:
            messages: 原始消息列表
            strategy: 压缩策略
                      - "last": 保留最后N条
                      - "first": 保留第一条（系统消息）
                      - "both": 保留第一条和最后N条
        
        Returns:
            压缩后的消息列表
        """
        if strategy == "last":
            # 保留最近的
            total_tokens = 0
            result = []
            for msg in reversed(messages):
                msg_tokens = self.estimate_tokens(msg["content"])
                if total_tokens + msg_tokens <= self.max_context_tokens - self.reserved_tokens:
                    result.insert(0, msg)
                    total_tokens += msg_tokens
                else:
                    break
            return result
        
        elif strategy == "both":
            # 保留系统消息和最近的
            if not messages:
                return []
            
            system_msg = messages[0] if messages[0]["role"] == "system" else None
            recent = self.compress_messages(
                messages[1:], strategy="last"
            )
            
            if system_msg:
                return [system_msg] + recent
            return recent
        
        return messages


# 使用示例
def multiturn_example():
    """多轮对话示例"""
    
    # 创建对话管理器
    manager = ConversationManager(
        client=client,
        model="gpt-5.4-mini",
        max_tokens=3000,
        system_prompt="你是一个知识渊博的AI助手。"
    )
    
    # 模拟多轮对话
    conversation = [
        ("user", "我喜欢历史，特别是中国古代史。"),
        ("assistant", "中国古代史确实很有趣！您对哪个朝代最感兴趣呢？"),
        ("user", "我最喜欢唐朝，能介绍一下吗？"),
        ("assistant", "唐朝（618-907年）是中国历史上最繁荣的朝代之一..."),
        ("user", "那唐朝的诗歌有哪些著名诗人？")
    ]
    
    for role, content in conversation:
        manager.add_message(role, content)
        print(f"{role}: {content[:30]}...")
    
    print(f"\n总token数: {manager.get_total_tokens()}")
    
    # 检查是否需要裁剪
    manager.trim_to_limit()
    print(f"裁剪后token数: {manager.get_total_tokens()}")
    
    # 获取相关上下文
    query = "唐朝的文化有什么特点？"
    relevant = manager.get_relevant_context(query, top_k=2)
    
    print("\n相关上下文:")
    for msg in relevant:
        print(f"  {msg.role}: {msg.content[:40]}...")
    
    # 发送消息
    manager.add_message("user", query)
    response = manager.client.chat.completions.create(
        model=manager.model,
        messages=manager.build_messages()
    )
    
    assistant_reply = response.choices[0].message.content
    manager.add_message("assistant", assistant_reply)
    
    print(f"\n助手回复: {assistant_reply[:100]}...")
