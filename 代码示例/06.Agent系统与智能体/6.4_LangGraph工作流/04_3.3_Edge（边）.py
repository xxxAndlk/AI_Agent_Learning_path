workflow.add_conditional_edges(
    "analyze",
    lambda s: s["next_step"],  # 条件函数，返回决定下一步走哪条路
    {
        "calculate": "calculate",
        "search": "search",
        "chat": "chat"
    }
)
