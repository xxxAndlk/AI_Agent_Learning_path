# -*- coding: utf-8 -*-
"""Agent 任务执行系统（第02课实战项目）：思考-行动-观察循环 + 工具箱，自主拆解任务并办完。

零依赖可跑（纯标准库，"思考"由规则模拟；接 LLM 只需替换 plan/decide 两步）：
    python agent_runner.py                    # 内置演示任务
    python agent_runner.py "帮我查报销标准"     # 自定任务
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 工具箱
# 每个工具 = 一个函数 + 一句说明（说明是给"大脑"看的，写清楚才选得对）
NOTES = []  # 简化备忘录；真实项目换成写文件/数据库


def tool_calc(expr):
    """四则运算。eval 前只放行数字与运算符，防误用。"""
    if not expr or any(ch not in "0123456789+-*/(). " for ch in expr):
        raise ValueError("只支持数字与 + - * / ( )")
    return f"计算结果 = {eval(expr)}"  # noqa: S307


def tool_add_note(text):
    NOTES.append(text)
    return f"已记录备忘（第 {len(NOTES)} 条）：{text}"


def tool_lookup(query):
    """查内置小知识库；生产中换成向量检索/真实 API。"""
    KB = {
        "加班": "加班晚餐报销上限 40 元，需 20:00 后",
        "住宿": "差旅住宿每晚上限 400 元",
        "vpn": "VPN 在 IT 服务台提工单申请，审批后邮件下发",
        "年假": "入职满一年每年 5 天，满三年 10 天",
    }
    hits = [v for k, v in KB.items() if k in query.lower() or k in query]
    return "；".join(hits) if hits else f"资料库中没有关于「{query}」的记录"


TOOLBOX = {
    "calc": (tool_calc, "做四则运算，参数是算式字符串，如 '400*3'"),
    "add_note": (tool_add_note, "把一段结论记入备忘录，参数是文字"),
    "lookup": (tool_lookup, "查公司制度资料，参数是关键词，如 '住宿'"),
}

# 关键词 -> 工具选择策略（规则模拟大脑；LLM 版改成让模型输出 JSON）
# 顺序即优先级：先认"记备忘"，再认"算数"，最后兜底"查资料"——
# 否则"把合计记入备忘"会先撞上 calc 的"合计"、选错工具
PLAN_RULES = [
    (("记", "备忘", "记入", "提醒"), "add_note"),
    (("算", "算一下", "算出", "统计", "共", "合计", "上限"), "calc"),
    (("查", "查一下", "了解", "标准", "流程", "多少"), "lookup"),
]


# ---------------------------------------------------------------- Agent
def plan(goal):
    """把总任务拆成子任务。规则版：按分句切；LLM 版：让模型输出 JSON 计划。"""
    subs = [s.strip("。？！；;， ") for s in goal.replace("，", "。").split("。")]
    subs = [s for s in subs if s]
    return subs if len(subs) >= 2 else [goal]


def choose_tool(sub):
    """思考环节：该子任务最像要调哪个工具？按 PLAN_RULES 顺序命中第一个。"""
    for keys, tool in PLAN_RULES:
        if any(k in sub for k in keys):
            return tool
    return "lookup"  # 默认先查资料


def extract_arg(sub, tool):
    """从子任务里抠参数：数字串给 calc，其余给 lookup/add_note。"""
    if tool == "calc":
        num = "".join(ch for ch in sub if ch.isdigit() or ch in "+-*/().")
        return num if num else "0"
    if tool == "add_note":
        for ch in "记一下记住把记入记到备忘录备忘：:，。":
            sub = sub.replace(ch, "")
        return sub.strip() or "（空备忘）"
    return sub


def run(goal):
    """主循环：拆解 -> 逐个子任务走一轮"思考-行动-观察" -> 汇报。"""
    history = []  # 滚动上下文：Agent 的短期记忆
    print("=" * 50)
    print(f"总任务：{goal}\n")
    for i, sub in enumerate(plan(goal), 1):
        thought = choose_tool(sub)  # 思考
        tool, desc = TOOLBOX[thought]
        arg = extract_arg(sub, thought)
        print(f"[{i}] 子任务：{sub}")
        print(f"    思考：这一步要「{sub[:12]}…」→ 调用 {thought}（{desc}）")
        try:
            obs = tool(arg)  # 行动
        except Exception as e:
            obs = f"工具出错：{e}"  # 观察：失败也是观察，不能让循环崩掉
        print(f"    行动：{thought}({arg!r})")
        print(f"    观察：{obs}\n")
        history.append((sub, obs))
    print("-" * 50)
    print("任务完成，汇报：")
    for sub, obs in history:
        print(f"  · {sub} -> {obs}")


def demo():
    run("查一下差旅住宿标准，算一下 400*3 是多少，把合计 1200 记入备忘")


def main():
    goal = " ".join(sys.argv[1:]).strip()
    run(goal) if goal else demo()


if __name__ == "__main__":
    main()
