"""llm_eval_demo.py —— 最小 LLM 评测：迷你问答集上算规则指标 + 与"人工"打分对照。纯标准库离线真跑。

运行：python llm_eval_demo.py
（对应第 11 章第 05 课；评测分数即第 12 章第 04 课 Dashboard"质量趋势"面板的数据源）
"""
EVAL_SET = [
    {"qid": "Q1", "question": "团建费用谁出？", "keywords": ["公司", "承担"], "lo": 8, "hi": 60, "need_digit": False},
    {"qid": "Q2", "question": "报销多久到账？", "keywords": ["审批", "5", "工作日"], "lo": 8, "hi": 60, "need_digit": True},
    {"qid": "Q3", "question": "年假过期还能补吗？", "keywords": ["3 月", "补休"], "lo": 8, "hi": 60, "need_digit": True},
]

# 两个候选版本对同一份考卷的回答（模拟模型输出，无需 API Key）
CANDIDATES = {
    "v1": {
        "Q1": "团建的话一般是大家一起想办法解决。",
        "Q2": "很快的，提交之后等消息就行了。",
        "Q3": "年假过期就不能休了，所以要提前安排。",
    },
    "v2": {
        "Q1": "团建费用由公司承担。",
        "Q2": "主管审批通过后 5 个工作日内到账。",
        "Q3": "次年 3 月底前可以补休，过期作废。",
    },
}

# "人工"打分： pretend 三位同事按 1~5 量表（1胡说/3能用/5惊艳）打的平均分
MANUAL_SCORES = {
    "v1": {"Q1": 2.7, "Q2": 1.3, "Q3": 3.0},
    "v2": {"Q1": 5.0, "Q2": 5.0, "Q3": 4.7},
}


def auto_score(answer: str, item: dict) -> tuple[float, str]:
    """规则指标合成 0~5 自动分：关键词命中(3分) + 长度(1分) + 格式(1分)。返回(分数, 扣分说明)。"""
    hits = sum(1 for k in item["keywords"] if k in answer)
    kw = hits / len(item["keywords"]) * 3
    notes = []
    if hits < len(item["keywords"]):
        notes.append(f"关键词{hits}/{len(item['keywords'])}")
    length_ok = item["lo"] <= len(answer) <= item["hi"]
    if not length_ok:
        notes.append(f"长度{len(answer)}字不在[{item['lo']},{item['hi']}]")
    fmt_ok = (not item["need_digit"]) or any(c.isdigit() for c in answer)
    if not fmt_ok:
        notes.append("涉及时效却没带数字")
    return round(kw + length_ok + fmt_ok, 2), "；".join(notes) or "全过"


def evaluate(candidate: str) -> list[dict]:
    rows = []
    for item in EVAL_SET:
        ans = CANDIDATES[candidate][item["qid"]]
        score, note = auto_score(ans, item)
        rows.append({"qid": item["qid"], "answer": ans, "auto": score,
                     "manual": MANUAL_SCORES[candidate][item["qid"]], "note": note})
    return rows


def main() -> None:
    print("== 迷你评测集：3 题，两个候选版本，自动指标 vs 人工打分 ==\n")
    summary = {}
    for cand in ("v1", "v2"):
        print(f"--- 候选 {cand} ---")
        rows = evaluate(cand)
        for r in rows:
            print(f"{r['qid']} 自动分 {r['auto']:.1f} | 人工 {r['manual']:.1f} | {r['note']}")
            print(f"     回答：{r['answer']}")
        avg_auto = sum(r["auto"] for r in rows) / len(rows)
        avg_manual = sum(r["manual"] for r in rows) / len(rows)
        dev = sum(abs(r["auto"] - r["manual"]) for r in rows) / len(rows)
        summary[cand] = (avg_auto, avg_manual)
        print(f"均分：自动 {avg_auto:.2f} / 人工 {avg_manual:.2f}（两者平均偏差 {dev:.2f}）\n")

    winner_auto = max(summary, key=lambda c: summary[c][0])
    winner_manual = max(summary, key=lambda c: summary[c][1])
    print(f"自动指标选出 {winner_auto}，人工也选 {winner_manual} -> "
          + ("排序一致，指标有效，可放心用于粗筛。" if winner_auto == winner_manual else "排序打架，先修指标再信它。"))
    print("决策：分数达标才发版（呼应第02课 candidate->production 的'评估通过'）。")


if __name__ == "__main__":
    main()
