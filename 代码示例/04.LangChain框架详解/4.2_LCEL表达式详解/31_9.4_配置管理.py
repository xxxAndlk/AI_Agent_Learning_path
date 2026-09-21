"""
LCEL配置管理最佳实践
展示如何灵活配置LCEL应用
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableConfig
import os
from dataclasses import dataclass
from typing import Optional

# ============================================================
# 方式1：使用环境变量
# ============================================================

# 配置LLM
llm = ChatOpenAI(
    model=os.getenv("LLM_MODEL", "gpt-5.4-mini"),
    temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
    max_tokens=int(os.getenv("LLM_MAX_TOKENS", "1000")),
    api_key=os.getenv("OPENAI_API_KEY")
)

# ============================================================
# 方式2：使用配置类
# ============================================================

@dataclass
class ChainConfig:
    """链配置数据类"""
    llm_model: str = "gpt-5.4-mini"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 1000
    max_retries: int = 3
    timeout: int = 60
    enable_streaming: bool = True

def create_configured_chain(config: ChainConfig):
    """根据配置创建链"""
    
    llm = ChatOpenAI(
        model=config.llm_model,
        temperature=config.llm_temperature,
        max_tokens=config.llm_max_tokens,
        streaming=config.enable_streaming
    )
    
    prompt = ChatPromptTemplate.from_template("{question}")
    
    chain = (
        prompt
        | llm
        | StrOutputParser()
    )
    
    # 可以添加配置到链的metadata中
    chain.config = config
    
    return chain

# 使用配置
prod_config = ChainConfig(
    llm_model="gpt-5.4",
    llm_temperature=0.5,
    max_retries=5
)
prod_chain = create_configured_chain(prod_config)

# ============================================================
# 方式3：使用RunnableConfig运行时配置
# ============================================================

chain = (
    ChatPromptTemplate.from_template("{question}")
    | ChatOpenAI()
    | StrOutputParser()
)

# 运行时配置
config = RunnableConfig(
    tags=["production", "qa"],      # 用于追踪和过滤
    metadata={"version": "1.0"},    # 元数据
    callbacks=[],                   # 回调处理器
    recursion_limit=100             # 递归限制
)

# 执行时传入配置
result = chain.invoke({"question": "测试"}, config=config)

# ============================================================
# 方式4：条件配置
# ============================================================

def get_llm_by_environment():
    """根据环境选择LLM"""
    env = os.getenv("ENV", "development")
    
    if env == "production":
        return ChatOpenAI(model="gpt-5.4", temperature=0.5)
    elif env == "staging":
        return ChatOpenAI(model="gpt-5.4-mini", temperature=0.3)
    else:
        return ChatOpenAI(model="gpt-5.4-mini", temperature=0.9)

llm = get_llm_by_environment()
print(f"当前环境使用的模型: {llm.model_name}")
