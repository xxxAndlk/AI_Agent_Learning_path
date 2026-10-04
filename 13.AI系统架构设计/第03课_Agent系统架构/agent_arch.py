# agent_arch.py —— Agent 系统架构骨架（第13章第03课配套）
# 用途：纯标准库演示运行时循环 + 状态结构 + 工具注册表 + 记忆（含 json 落盘）
# 运行：python agent_arch.py   零依赖零Key，直接真跑

import json
import os
import tempfile

MAX_STEPS = 6  # 运行时刹车：步数上限（想一想③可改成 2 观察强制收尾）


# ============ 工具层：注册表 ============
TOOLS = {
    "query_sales": {
        "desc": "查询销售数据。参数：quarter（如 2026Q1）",
        "level": "read",
        "fn": lambda quarter: {"2026Q1": 120, "2026Q2": 135, "2025Q1": 100}.get(quarter, 0),
    },
    "query_plan": {
        "desc": "查询销售目标。参数：quarter",
        "level": "read",
        "fn": lambda quarter: 125 if quarter == "2026Q1" else 130,
    },
    "write_report": {
        "desc": "提交报告（演示用，只打印不落盘）。参数：text",
        "level": "write",  # 写操作：真实系统需人工确认
        "fn": lambda text: f"报告已提交（{len(text)}字）",
    },
}


# ============ 状态：工作笔记 ============
def new_state(goal):
    return {"goal": goal, "steps": [], "budget_left": MAX_STEPS, "done": False, "answer": ""}


def remember_context(state):
    """把状态压成模型能看懂的上下文（真实系统拼进提示词）。"""
    lines = [f"目标：{state['goal']}"]
    for s in state["steps"]:
        lines.append(f"已做：{s['think']} -> {s['act']} -> {str(s['obs'])[:40]}")
    return "\n".join(lines)


# ============ 长期记忆：json 落盘 ============
def load_memory():
    path = os.path.join(tempfile.gettempdir(), "agent_ltm.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {"lessons": []}


def save_memory(mem):
    path = os.path.join(tempfile.gettempdir(), "agent_ltm.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False)


# ============ 运行时：主循环 ============
def run(goal):
    state = new_state(goal)
    mem = load_memory()
    print(f"[运行时] 接收任务：{goal}")
    while not state["done"] and state["budget_left"] > 0:
        state["budget_left"] -= 1
        # 思考：真实系统由 LLM 决策；本课用规则模拟"看状态选工具"
        ctx = remember_context(state)
        if "目标" in ctx and len(state["steps"]) == 0:
            think, tool, args = "先查实际销售数据", "query_sales", {"quarter": "2026Q1"}
        elif len(state["steps"]) == 1:
            think, tool, args = "对比需要目标值，再查目标", "query_plan", {"quarter": "2026Q1"}
        else:
            think, tool, args = "数据齐了，写总结报告", "write_report", {"text": "Q1 完成 120/125，达成 96%"}
        print(f"[思考] {think}（剩余步数 {state['budget_left']}）")
        # 行动：查注册表 + 权限检查 + 统一错误处理
        entry = TOOLS[tool]
        if entry["level"] == "write":
            print("[安全] 写操作：生产系统此处应请求人工确认（演示自动放行）")
        try:
            obs = entry["fn"](**args)
        except Exception as e:  # 错误也当观察喂回去，让下一轮自己调整
            obs = f"工具出错：{e}"
        print(f"[行动] {tool}({args}) -> [观察] {obs}")
        state["steps"].append({"think": think, "act": tool, "obs": obs})
        if tool == "write_report":
            state["done"], state["answer"] = True, obs
    # 刹车触发：体面收尾而不是半途而废
    if not state["done"]:
        state["answer"] = "（步数预算耗尽，已收尾：以下是目前的进展…" + remember_context(state)[-40:] + "）"
        print(f"[运行时] ⚠ 刹车触发，强制收尾")
    # 记忆沉淀：长期记忆记一条经验，跨任务复用
    mem["lessons"].append({"goal": goal, "steps_used": len(state["steps"])})
    save_memory(mem)
    print(f"[记忆] 长期记忆已落盘，累计 {len(mem['lessons'])} 条任务经验")
    print(f"[产出] {state['answer']}")
    return state


if __name__ == "__main__":
    print("=" * 60)
    print("演示：完整运行时循环（思考-行动-观察 × N，带刹车与记忆）")
    print("=" * 60)
    run("对比 2026Q1 销售完成情况并写总结")
    print()
    os.remove(os.path.join(tempfile.gettempdir(), "agent_ltm.json"))  # 演示数据不留残留
