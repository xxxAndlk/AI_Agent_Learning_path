# 1. 限制工具数量
# 推荐：每个Agent使用5-10个相关工具
# 避免：在一个Agent中放置过多不相关的工具

# 2. 优化工具描述
@tool
def well_described_tool(param: str) -> str:
    """清晰描述工具用途
    
    Args:
        param: 参数说明
        
    Returns:
        返回值说明
    """
    return ""

# 3. 使用早期停止
# v1.x 中 create_agent 内部基于 LangGraph 自动管理停止逻辑
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="你是一个智能助手。"
)

# 4. 限制最大迭代步数（替代旧版 max_iterations，防止无限循环）
# result = agent.invoke(
#     {"messages": [{"role": "user", "content": "问题"}]},
#     config={"recursion_limit": 50},
# )

# 5. 使用流式输出提升用户体验（stream_mode="messages" 逐 token 流式）
for msg, _metadata in agent.stream(
    {"messages": [{"role": "user", "content": "问题"}]},
    stream_mode="messages",
):
    if msg.content:
        print(msg.content, end="", flush=True)
