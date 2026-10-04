# -*- coding: utf-8 -*-
# 用途：用纯标准库模拟 Agent 的"思考-行动-观察"核心循环，看清 Agent 的最简骨架。
# 依赖：仅 Python 标准库；运行：python agent_intro.py
# 说明：真实 Agent 的"思考"由大模型完成；本脚本离线运行，用几条 if 规则扮演
#       模型，让你专注看清循环本身的形状——真实系统里只需把 think() 换成模型调用。

import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 控制台防中文乱码
except Exception:
    pass

MAX_STEPS = 5  # 安全阀：最多走几步就强制停下，防止 Agent 绕圈"跑飞"（第03课细讲）

# ---------- 第 1 部分：工具箱 ----------
# Agent 能"动手"的本钱就是这些工具。关键习惯：先登记造册（名字 -> 函数），
# 大脑只报名字，执行器负责按名字找到函数——解耦后换工具不用改大脑。

def get_weather(city):
    fake = {"北京": "晴，25°C", "上海": "小雨，19°C"}
    return fake.get(city, f"{city}：多云，22°C")

def get_clothes_advice(temp_c):
    if temp_c >= 24:
        return "短袖就行"
    if temp_c >= 15:
        return "薄外套合适"
    return "注意保暖"

TOOLS = {"get_weather": get_weather, "get_clothes_advice": get_clothes_advice}

# ---------- 第 2 部分："大脑" ----------
# 真实系统：把任务、历史、工具清单发给大模型，它输出"下一步做什么"。
# 离线演示：用规则模拟模型决策，输出格式与真实模型一致（动作名 + 参数）。

def think(memory):
    """看一眼已有的观察，决定下一步：返回 (动作名, 参数) 或 ('finish', 答案)。"""
    weather = next((o for _, o in memory if "°C" in o), None)
    if weather is None:                      # 还不知道天气 -> 先查
        return "get_weather", "北京"
    advice = next((o for _, o in memory if "穿" in o or "袖" in o), None)
    if advice is None:                       # 天气有了 -> 再问穿衣建议
        temp = float(weather.split("，")[1].replace("°C", ""))
        return "get_clothes_advice", temp
    return "finish", f"{weather}，{advice}。任务完成！"

# ---------- 第 3 部分：核心循环 ----------
def run_agent(task):
    print(f"【任务】{task}\n")
    memory = []                              # 观察记录；下一课它会升级成真正的记忆
    for step in range(1, MAX_STEPS + 1):
        action, arg = think(memory)
        if action == "finish":
            print(f"【最终答案】{arg}")
            return arg
        print(f"思考：我需要调用 {action}")
        print(f"行动：{action}({arg!r})")
        observation = TOOLS[action](arg)     # 真正"动手"的地方
        print(f"观察：{observation}\n")
        memory.append((action, observation))
    print("已达步数上限，强制停止——Agent 也是会跑丢的。")
    return None

if __name__ == "__main__":
    # 对照组：普通链——每一步都写死，没有思考、没有变通
    print("【对照组·普通链】")
    w = get_weather("北京")
    print(f"普通链输出：{w}；短袖就行（第二步的 25°C 是你写死的，它自己不会看）\n")
    # Agent 版：目标固定，怎么走让它自己想
    run_agent("北京今天穿什么合适？")
