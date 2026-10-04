# -*- coding: utf-8 -*-
"""Multi-Agent 协作与企业助手（第06课实战项目）：主管拆解分派、工人各司其职、补派自检、汇总交付。

零依赖可跑（纯标准库，"思考"由规则模拟；接 LLM 只需把拆解/工人换成模型调用）：
    python multi_agent_app.py               # 内置演示：季度营收简报
    python multi_agent_app.py "新员工入职指引"  # 换个企业需求再跑
"""

import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 知识与数据
KB = {
    "年假": "年假：入职满一年每年 5 天，满三年 10 天，满五年 15 天",
    "报销": "报销：票据需在费用发生后 10 个工作日内提交，住宿上限每晚 400 元",
    "入职": "入职：报到当天签合同办门禁，账号权限由 IT 在 1 个工作日内开通",
    "营收": "本月营收 ¥320 万，环比 +8%；差旅费用 ¥41 万，环比 -5%",
}

# ---------------------------------------------------------------- 工人
# 每个工人 = 一个函数 + 一句话职责。对主管来说，工人就是它的"工具"。
def clean_title(text):
    """从任务描述剥出干净标题：去动词前缀、只取第一句。"""
    t = text.split("，")[0]
    for w in ("请帮我", "写一份", "写个", "帮我", "写", "起草"):
        if t.startswith(w):
            t = t[len(w):]
            break
    return t.strip() or "工作简报"


def worker_research(topic):
    """检索员：查公司制度/数据，只管查原文。"""
    for k, fact in KB.items():
        if k in topic:
            return fact
    return f"「{topic}」未检索到制度依据"


def worker_analyst(expr):
    """分析员：算数。数字从任务里抠出来。"""
    num = "".join(ch for ch in str(expr) if ch.isdigit() or ch in "+-*/().")
    if not num:
        return "分析员：没有拿到可计算的数字，需要先提供数据"
    return f"分析结果：{num} = {eval(num)}"  # noqa: S307


def worker_writer(title, material=""):
    """文案：按企业口吻模板起草。模板定骨架，LLM 版让模型填肉。"""
    return (f"《{clean_title(title)}》\n"
            f"各位同事好，本期要点如下：{material or '详见正文'}。\n"
            f"如有疑问请联系对应负责人，谢谢！")


AGENTS = {
    "检索员": (worker_research, "查公司制度与数据原文"),
    "分析员": (worker_analyst, "对数字做计算"),
    "文案":   (worker_writer, "按企业口吻起草文本"),
}

# 子任务关键词 -> 工人（顺序即优先级：先认"要产出文本"，再认"要查料"，最后"要算数"——
# 否则"写一份营收简报"会先撞上检索员的"营收"、派错人）
ROUTE_RULES = [
    (("写", "起草", "简报", "指引", "报告", "通知"), "文案"),
    (("查", "制度", "依据", "数据", "营收", "费用"), "检索员"),
    (("算", "合计", "环比", "增长", "%", "总计"), "分析员"),
]


# ---------------------------------------------------------------- 主管
def route(sub):
    """主管思考：这个子任务派给谁？"""
    for keys, agent in ROUTE_RULES:
        if any(k in sub for k in keys):
            return agent
    return "检索员"  # 默认先查料


def split_task(goal):
    """拆任务：按分句切。LLM 版改成让模型输出 JSON 计划（第3章 Structured Output）。"""
    subs = [s.strip("。？！；;， ") for s in goal.replace("，", "。").split("。")]
    return [s for s in subs if s] or [goal]


def supervise(goal):
    """主管主循环：拆解 -> 派工 -> 自检补派 -> 汇总。"""
    ledger = []   # 派工台账：谁、干什么、交回什么
    subs = split_task(goal)
    print("=" * 54)
    print(f"企业需求：{goal}")
    print(f"主管拆解出 {len(subs)} 个子任务\n")

    for i, sub in enumerate(subs, 1):
        agent = route(sub)
        func, duty = AGENTS[agent]
        try:
            result = func(sub)
        except Exception as e:
            result = f"工人出错：{e}"
        ledger.append({"sub": sub, "agent": agent, "result": result})
        print(f"[{i}] {sub}")
        print(f"    派给 {agent}（{duty}）")
        print(f"    交回：{result}\n")

    # 自检补派：发现"分析结果无数据"就追加一次检索（生产中这类闭环是可靠性关键）
    fixed = []
    for item in ledger:
        fixed.append(item)
        if "没有拿到可计算的数字" in item["result"] or "未检索到" in item["result"]:
            patch_sub = f"补查「{item['sub'][:10]}」的数据"
            result = worker_research("营收")
            fixed.append({"sub": patch_sub, "agent": "检索员", "result": result})
            print(f"[补派] 检测到缺料：{patch_sub}")
            print(f"    派给 检索员 -> 交回：{result}\n")

    report = assemble(goal, fixed)
    print("-" * 54)
    print("最终交付：")
    print(report)
    print(f"\n（派工台账 {len(fixed)} 条，可接入第 04 课的监控采集）")
    return report


def assemble(goal, ledger):
    """汇总：把各工人产出去重后拼成一份带依据的企业交付物。"""
    seen, facts = [], []
    for x in ledger:
        r = x["result"]
        if "检索" in x["agent"] and "未检索" not in r and r not in seen:
            seen.append(r)
            facts.append(r)
    return worker_writer(clean_title(goal), "；".join(facts) or "详见各分项")


def demo():
    supervise("写一份季度营收简报，查一下本月营收数据，算一下环比增长")


def main():
    goal = " ".join(sys.argv[1:]).strip()
    if goal:
        supervise(goal)
    else:
        demo()


if __name__ == "__main__":
    main()
