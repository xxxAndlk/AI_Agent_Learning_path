# v1.x 中使用 create_agent，max_iterations 等参数通过配置传递
# 旧版 AgentExecutor 已被 create_agent 取代
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个有用的AI助手。"
)
# create_agent 内部基于 LangGraph，自动处理循环和停止逻辑
