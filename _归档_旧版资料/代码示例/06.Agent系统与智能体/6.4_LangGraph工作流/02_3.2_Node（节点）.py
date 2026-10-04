def analyze_query(state: AgentState) -> AgentState:
    """分析查询节点"""
    query = state["query"]
    
    # 分析查询类型
    if "计算" in query or "多少" in query:
        state["next_step"] = "calculate"
    elif "搜索" in query or "查询" in query:
        state["next_step"] = "search"
    else:
        state["next_step"] = "chat"
    
    state["messages"].append({"role": "system", "content": f"分析结果: 使用{state['next_step']}处理"})
    return state
