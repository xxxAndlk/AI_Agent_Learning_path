"""
带记忆和工具的聊天机器人 (v1.x 版本)
"""
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import create_agent
from langchain.tools import Tool
from langgraph.checkpoint.memory import InMemorySaver

from config import LLM_MODEL


class ChatBot:
    """聊天机器人"""
    
    def __init__(
        self,
        llm: Optional[ChatOpenAI] = None,
        model_name: str = LLM_MODEL,
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化聊天机器人
        
        Args:
            llm: 语言模型
            model_name: 模型名称
            temperature: 温度参数
            system_prompt: 系统提示词
        """
        self.llm = llm or ChatOpenAI(
            model=model_name,
            temperature=temperature,
        )
        
        # 默认系统提示词
        self.system_prompt = system_prompt or """你是一个友好的 AI 助手。
你具有以下能力：
1. 记住对话历史，在适当的时候引用之前的对话
2. 使用各种工具来完成用户请求
3. 提供准确、有帮助的回答

请用友好、专业的方式与用户交流。"""
        
        # 初始化记忆（v1.x：LangGraph checkpointer 管理 Agent 对话状态）
        self.checkpointer = InMemorySaver()
        
        # 工具列表
        self.tools: List[Tool] = []
        self.agent = None
        
        # 初始化代理
        self._initialize_agent()
    
    def _initialize_agent(self):
        """初始化 Agent"""
        if self.tools:
            # v1.x 使用 create_agent，通过 system_prompt 参数设置提示词
            self.agent = create_agent(
                model=self.llm,
                tools=self.tools,
                system_prompt=self.system_prompt,
                checkpointer=self.checkpointer,
            )
    
    def add_tool(self, tool: Tool):
        """添加工具"""
        self.tools.append(tool)
        self._initialize_agent()
    
    def chat(self, message: str) -> str:
        """
        聊天
        
        Args:
            message: 用户消息
            
        Returns:
            AI 回复
        """
        if self.agent:
            # 使用 Agent 执行（v1.x：messages 输入 + thread_id 会话隔离）
            result = self.agent.invoke(
                {"messages": [{"role": "user", "content": message}]},
                config={"configurable": {"thread_id": "default"}},
            )
            return result["messages"][-1].content
        else:
            # 简单对话
            response = self.llm.invoke(message)
            return response.content
    
    def clear_memory(self):
        """清空记忆（重建 checkpointer 并重置 Agent）"""
        self.checkpointer = InMemorySaver()
        self._initialize_agent()
    
    def get_history(self) -> List[Any]:
        """获取对话历史（从 LangGraph 检查点状态读取消息）"""
        if self.agent is None:
            return []
        state = self.agent.get_state({"configurable": {"thread_id": "default"}})
        return state.values.get("messages", [])


# 工具定义
def get_weather(city: str) -> str:
    """获取天气信息（模拟）"""
    weather_data = {
        "北京": "晴，15-25°C",
        "上海": "多云，18-27°C",
        "广州": "小雨，22-30°C",
        "深圳": "晴，23-31°C",
    }
    return weather_data.get(city, f"未找到 {city} 的天气信息")


def calculate(expression: str) -> str:
    """数学计算"""
    try:
        result = eval(expression)
        return str(result)
    except Exception as e:
        return f"计算错误: {str(e)}"


def search_wiki(query: str) -> str:
    """搜索维基百科（模拟）"""
    return f"关于 '{query}' 的信息：这是一段模拟的维基百科内容。"


# 创建工具
weather_tool = Tool(
    name="weather",
    func=get_weather,
    description="获取指定城市的天气信息。输入：城市名称（如：北京）",
)

calculator_tool = Tool(
    name="calculator",
    func=calculate,
    description="进行数学计算。输入：数学表达式（如：2+2*3）",
)

wiki_tool = Tool(
    name="wiki_search",
    func=search_wiki,
    description="搜索维基百科。输入：搜索关键词",
)


# 应用入口
if __name__ == "__main__":
    # 创建聊天机器人
    chatbot = ChatBot()
    
    # 添加工具
    chatbot.add_tool(weather_tool)
    chatbot.add_tool(calculator_tool)
    chatbot.add_tool(wiki_tool)
    
    # 对话测试
    print("=== 聊天机器人测试 ===")
    
    # 测试基本对话
    response1 = chatbot.chat("你好，请介绍一下自己")
    print(f"用户: 你好，请介绍一下自己")
    print(f"AI: {response1}\n")
    
    # 测试工具调用
    response2 = chatbot.chat("北京今天天气怎么样？")
    print(f"用户: 北京今天天气怎么样？")
    print(f"AI: {response2}\n")
    
    # 测试计算
    response3 = chatbot.chat("请帮我计算 123 * 456")
    print(f"用户: 请帮我计算 123 * 456")
    print(f"AI: {response3}\n")
    
    # 测试记忆
    response4 = chatbot.chat("我刚才问你什么问题？")
    print(f"用户: 我刚才问你什么问题？")
    print(f"AI: {response4}\n")
    
    # 查看对话历史
    print("=== 对话历史 ===")
    for msg in chatbot.get_history():
        print(f"{type(msg).__name__}: {msg.content[:50]}...")
