# -*- coding: utf-8 -*-
# 用途：演示最简状态流转——第1部分用纯标准库手工模拟 StateGraph（离线可跑），
#       第2部分用真正的 langgraph 库搭同一张图（缺库打印中文提示并跳过）。
# 依赖：第 1 部分仅 Python 标准库；第 2 部分需 pip install langgraph（不需要 API Key）

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台防中文乱码
except Exception:
    pass

# ---------- 共用的节点逻辑：客服分流图 ----------
# 状态（State）就是在节点间传递的数据包；节点读它、改它、还回去。

def classify(state):
    q = state["query"]
    if "天气" in q:
        state["category"] = "weather"
    elif any(k in q for k in ("加", "减", "乘", "除", "算")):
        state["category"] = "math"
    else:
        state["category"] = "chat"
    print(f"  [classify] 识别类别 -> {state['category']}")
    return state

def weather_node(state):
    state["answer"] = "今天晴，25°C，适合出门（演示数据）。"
    print("  [weather_node] 生成天气回答")
    return state

def math_node(state):
    state["answer"] = "3 加 5 等于 8（演示计算）。"
    print("  [math_node] 生成计算回答")
    return state

def chat_node(state):
    state["answer"] = "我是演示客服，什么都能聊两句。"
    print("  [chat_node] 生成闲聊回答")
    return state

def route(state):
    """条件边的路由函数：看状态里的 category，决定下一步走哪个节点。"""
    return {"weather": "weather_node", "math": "math_node", "chat": "chat_node"}[state["category"]]

# ---------- 第 1 部分：手工模拟 StateGraph（离线真跑） ----------

class MiniGraph:
    """把 LangGraph 的核心玩法压缩到 20 行：登记节点、连边、按图走路。"""

    def __init__(self):
        self.nodes, self.conditional, self.entry = {}, {}, None

    def add_node(self, name, fn):
        self.nodes[name] = fn
        return self

    def set_entry(self, name):
        self.entry = name
        return self

    def add_conditional_edges(self, name, router):
        self.conditional[name] = router
        return self

    def invoke(self, state, max_steps=10):
        current, steps = self.entry, 0
        while current is not None and steps < max_steps:   # 走到没有出边 = END
            print(f"-> 进入节点 {current}")
            state = self.nodes[current](state)             # 节点处理数据包
            current = self.conditional.get(current, lambda s: None)(state)
            steps += 1
        return state

def part1_offline():
    print("=" * 52)
    print("第 1 部分：手工模拟版（离线真跑，不依赖任何第三方库）")
    g = (MiniGraph()
         .add_node("classify", classify)
         .add_node("weather_node", weather_node)
         .add_node("math_node", math_node)
         .add_node("chat_node", chat_node)
         .set_entry("classify")
         .add_conditional_edges("classify", route))
    for q in ("北京今天天气怎么样？", "帮我算 3 加 5", "随便聊聊天"):
        print(f"\n问题：{q}")
        result = g.invoke({"query": q, "category": "", "answer": ""})
        print(f"  最终回答：{result['answer']}")

# ---------- 第 2 部分：真正的 LangGraph（缺库中文提示跳过） ----------

def part2_real_langgraph():
    try:
        from langgraph.graph import StateGraph, START, END
        from typing import TypedDict
    except ImportError:
        print("\n[跳过] 第2部分需要 langgraph：pip install langgraph（本部分不需要 API Key）")
        return
    print("\n" + "=" * 52)
    print("第 2 部分：真正的 LangGraph（同一张图，交给框架执行）")

    class State(TypedDict):
        query: str
        category: str
        answer: str

    builder = StateGraph(State)
    builder.add_node("classify", classify)
    builder.add_node("weather_node", weather_node)
    builder.add_node("math_node", math_node)
    builder.add_node("chat_node", chat_node)
    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route)
    for name in ("weather_node", "math_node", "chat_node"):
        builder.add_edge(name, END)
    graph = builder.compile()          # 画完的图要"编译"才能跑
    result = graph.invoke({"query": "北京今天天气怎么样？", "category": "", "answer": ""})
    print(f"\n  最终回答：{result['answer']}")

if __name__ == "__main__":
    part1_offline()
    part2_real_langgraph()
