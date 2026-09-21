# v1.x 中 create_agent 的高级配置
from langchain.agents import create_agent

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个智能助手。",
    
    # LangGraph 配置（create_agent 内部基于 LangGraph）
    # 状态持久化、断点恢复等通过 LangGraph 配置实现
    
    # 调试
    # verbose=True,  # 通过回调或 LangSmith 实现可观测性
)

# 旧版 AgentExecutor 的配置项在 v1.x 中的对应方式：
# - max_iterations: 由 LangGraph 内部管理
# - max_execution_time: 通过 invoke 的超时参数控制
# - handle_parsing_errors: 通过 Middleware 或 try/except 处理
# - return_intermediate_steps: 通过 LangSmith 追踪查看
