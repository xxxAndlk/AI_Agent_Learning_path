from langchain.callbacks.base import BaseCallbackHandler
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.outputs import LLMResult
from typing import Any, Dict, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentCallbackHandler(BaseCallbackHandler):
    """自定义回调处理器"""
    
    def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
        """Agent执行动作时触发"""
        logger.info(f"🛠️ Agent执行动作: {action.tool}")
        logger.info(f"   参数: {action.tool_input}")
    
    def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
        """Agent完成时触发"""
        logger.info(f"✅ Agent完成")
        logger.info(f"   输出: {finish.return_values['output'][:100]}...")
    
    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """LLM开始推理时触发"""
        logger.info(f"🧠 LLM开始推理...")
    
    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """LLM完成推理时触发"""
        logger.info(f"🧠 LLM完成推理")
    
    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """工具开始执行时触发"""
        logger.info(f"🔧 工具开始: {serialized.get('name', 'unknown')}")
    
    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """工具执行完成时触发"""
        logger.info(f"🔧 工具完成，结果: {output[:100]}...")

# 使用回调处理器（v1.x 方式）
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

@tool
def simple_tool(query: str) -> str:
    """简单工具"""
    return f"处理: {query}"

llm = ChatOpenAI(model="gpt-5.4")
agent = create_agent(
    model=llm,
    tools=[simple_tool],
    system_prompt="你是一个智能助手。",
    # 通过 config 注入回调
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "测试回调"}]},
    config={"callbacks": [AgentCallbackHandler()]}
)
