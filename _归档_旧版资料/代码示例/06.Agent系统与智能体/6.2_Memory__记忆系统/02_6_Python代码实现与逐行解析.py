import os

from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Message:
    """对话消息数据类
    
    用于存储单条对话消息的完整信息，包含角色、内容、时间戳和元数据。
    """
    role: str                         # 角色: system/user/assistant/tool
    content: str                      # 消息内容
    timestamp: datetime = field(default_factory=datetime.now)  # 创建时间，默认为当前时间
    metadata: Dict = field(default_factory=dict)  # 额外元数据，默认为空字典

class ConversationMemory:
    """对话记忆管理器
    
    管理多轮对话的历史消息，支持上下文窗口控制。
    提供消息添加、窗口维护、上下文获取等功能。
    """
    
    def __init__(self, max_messages: int = 20, max_tokens: int = 4000):
        """
        初始化对话记忆管理器
        
        参数:
            max_messages: 最大保留消息数，默认为20
            max_tokens: 最大token数估算值，默认为4000（约等于3000中文字符）
        """
        self.messages: List[Message] = []  # 存储消息的列表，初始化为空
        self.max_messages = max_messages   # 设置消息数量上限
        self.max_tokens = max_tokens       # 设置token数量上限
        self.system_prompt: str = ""       # 系统提示词，用于引导AI行为
    
    def set_system_prompt(self, prompt: str):
        """设置系统提示词
        
        系统提示词用于定义AI助手的角色和行为准则。
        
        参数:
            prompt: 系统提示词内容
        """
        self.system_prompt = prompt
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """添加消息到历史记录
        
        创建一个新的Message对象并添加到消息列表中，
        添加后自动调用窗口维护方法确保不超出限制。
        
        参数:
            role: 消息角色 (system/user/assistant/tool)
            content: 消息内容
            metadata: 可选的元数据字典
        """
        # 创建消息对象，role指定角色，content指定内容
        # metadata默认为空字典，如果传入了则使用传入值
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(message)  # 将消息追加到列表末尾
        
        # 维护窗口大小，确保消息数量和token数不超出限制
        self._maintain_window()
    
    def _maintain_window(self):
        """维护上下文窗口
        
        内部方法，用于在添加消息后检查并调整窗口大小。
        采用两种策略：消息数量限制和token数量限制。
        """
        # 策略1：限制消息数量
        # 当消息数超过上限时，删除最早的消息
        while len(self.messages) > self.max_messages:
            # 保留最早的system消息（索引0），只删除其他角色消息
            # 这样确保系统提示始终存在
            if len(self.messages) > 1:
                self.messages.pop(0)  # 移除列表第一个元素（最早的消息）
        
        # 策略2：基于token的滑动窗口
        # 估算方式：中文字符约等于1.5个token（中文tokenizer特点）
        total_tokens = sum(len(m.content) * 1.5 for m in self.messages)
        # 当token总数超过上限且消息数足够多时，持续删除旧消息
        while total_tokens > self.max_tokens and len(self.messages) > 2:
            self.messages.pop(0)  # 删除最早的消息
            # 重新计算token总数
            total_tokens = sum(len(m.content) * 1.5 for m in self.messages)
    
    def get_context(self) -> List[Dict]:
        """获取格式化的上下文
        
        将内部的消息列表转换为API调用所需的格式。
        包含系统提示和所有历史消息。
        
        返回:
            包含role和content的字典列表，可直接用于LLM API调用
        """
        context = []  # 初始化空列表
        
        # 添加系统提示到上下文开头
        if self.system_prompt:
            context.append({
                "role": "system",
                "content": self.system_prompt
            })
        
        # 遍历所有历史消息，转换为字典格式
        for msg in self.messages:
            context.append({
                "role": msg.role,
                "content": msg.content
            })
        
        return context  # 返回构建好的上下文列表
    
    def clear(self):
        """清空记忆
        
        清除所有消息历史，用于新会话开始或用户请求重置。
        保留系统提示词设置。
        """
        self.messages = []  # 将消息列表重置为空


class ChatSession:
    """对话会话管理器
    
    整合记忆管理和LLM API调用的完整会话类。
    负责处理用户输入、调用AI模型、存储回复的完整流程。
    """
    
    def __init__(self, memory: ConversationMemory = None):
        """
        初始化对话会话
        
        参数:
            memory: 对话记忆管理器实例，如果为None则创建新实例
        """
        # 使用传入的memory或创建新的ConversationMemory实例
        self.memory = memory or ConversationMemory()
        # 注意：此处需要OpenAI API Key，实际使用需配置
        # self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def chat(self, user_input: str) -> str:
        """
        进行一次对话交互
        
        流程：添加用户消息 → 获取上下文 → 调用API → 添加助手回复 → 返回结果
        
        参数:
            user_input: 用户输入的文本
            
        返回:
            AI助手的回复文本
        """
        # 步骤1：添加用户消息到记忆
        self.memory.add_message("user", user_input)
        
        # 步骤2：获取包含系统提示和历史消息的完整上下文
        messages = self.memory.get_context()
        
        # 步骤3：调用LLM API（此处为模拟调用）
        # 实际应用中需要调用 OpenAI 或其他 LLM API
        # response = self.client.chat.completions.create(
        #     model="gpt-5.4-mini",
        #     messages=messages
        # )
        
        # 模拟AI回复
        assistant_reply = self._mock_response(user_input, messages)
        
        # 步骤4：将助手回复添加到记忆，供后续对话使用
        self.memory.add_message("assistant", assistant_reply)
        
        return assistant_reply
    
    def _mock_response(self, user_input: str, messages: List[Dict]) -> str:
        """模拟AI响应（用于演示）"""
        # 检查是否询问名字
        if "名字" in user_input:
            # 查找历史消息中用户是否提到过名字
            for msg in messages:
                if msg["role"] == "user" and "叫" in msg["content"]:
                    # 提取名字
                    content = msg["content"]
                    if "我叫" in content:
                        name = content.split("我叫")[1].strip("。")
                        return f"你叫{name}，我记得！"
            return "抱歉，我不知道你的名字。"
        
        # 简单回复
        responses = {
            "你好": "你好！有什么我可以帮助你的吗？",
            "天气": "今天天气确实不错！",
        }
        
        for key, response in responses.items():
            if key in user_input:
                return response
        
        return "我明白了"


if __name__ == "__main__":
    # 创建记忆管理器，设置最多保留10条消息
    memory = ConversationMemory(max_messages=10)
    # 设置系统提示词，定义AI角色
    memory.set_system_prompt("你是一个 helpful 的AI助手。")
    
    # 创建会话实例
    session = ChatSession(memory)
    
    # 模拟多轮对话
    print("=== 多轮对话示例 ===\n")
    
    # 定义测试输入序列
    inputs = [
        "你好，我叫张三。",
        "我叫什么名字？",
        "今天天气不错。",
        "你还记得我的名字吗？"
    ]
    
    # 遍历输入，逐个进行对话
    for user_input in inputs:
        print(f"用户: {user_input}")
        reply = session.chat(user_input)
        print(f"助手: {reply}\n")
