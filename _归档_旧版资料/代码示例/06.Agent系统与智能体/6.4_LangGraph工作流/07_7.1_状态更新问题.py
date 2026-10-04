# 错误示例
def wrong_node(state):
    state["messages"] = [{"role": "user", "content": "hello"}]  # 覆盖而非追加
    return state

# 正确示例
def correct_node(state):
    state["messages"].append({"role": "user", "content": "hello"})  # 追加
    return state
