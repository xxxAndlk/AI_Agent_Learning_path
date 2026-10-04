# 创建工作流图
workflow = StateGraph(AgentState)

# 添加节点
workflow.add_node("analyze", analyze_query)
workflow.add_node("calculate", calculate)
# ... 更多节点

# 设置入口
workflow.set_entry_point("analyze")

# 添加边
workflow.add_conditional_edges(...)
workflow.add_edge(...)

# 编译成可执行图
compiled_graph = workflow.compile()

# 执行工作流
result = compiled_graph.invoke(initial_state)
