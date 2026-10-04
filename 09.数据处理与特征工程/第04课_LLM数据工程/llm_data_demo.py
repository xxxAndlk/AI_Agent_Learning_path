# -*- coding: utf-8 -*-
"""llm_data_demo.py —— 模拟 LLM 数据工程流水线：
纯标准库离线段（批量模板生成 + 规则质检）本机真跑；
真实 LLM 批量生成段需 API Key（pip install openai），未填则中文提示跳过，本课未实跑。"""

import json
import os

# ---------------- 离线段：批量模板生成 ----------------
# "种子模板"相当于人工写好的 few-shot 例子；槽位值相当于 LLM 扩写的多样性来源
TEMPLATES = [
    {"instruction": "把这句客服话术改得更友好", "input": "已经说三遍了，自己看说明书", "output": "好的，我一步步带您看～"},
    {"instruction": "给商品写一句促销文案", "input": "", "output": "{product}今日特价，买到就是赚到"},
    {"instruction": "把下述问题归类为售后/咨询/投诉", "input": "{question}", "output": "归类结果：{label}"},
]

SLOTS = {
    "{product}": ["保温杯", "蓝牙耳机", "颈椎按摩仪"],
    "{question}": ["我的快递三天没动", "这个怎么开发票", "客服都不回复我"],
    "{label}": ["售后", "咨询", "投诉"],
}


def batch_generate(templates, slots):
    """程序化批量生成：模板**任何字段**里的槽位 × 候选值，同下标的槽位一起填充。"""
    out = []
    for t in templates:
        present = sorted({ph for ph in slots for v in t.values() if ph in v})
        if not present:
            out.append(dict(t))
            continue
        n = len(slots[present[0]])
        for i in range(n):
            item = {}
            for k, f in t.items():
                s = f
                for ph in present:  # 同下标槽位一起填，如 question[i] 配 label[i]
                    s = s.replace(ph, slots[ph][i % len(slots[ph])])
                item[k] = s
            out.append(item)
    return out


# ---------------- 离线段：规则质检（长度/缺字段/空转） ----------------
def quality_check(item):
    """返回错误列表，空列表=合格。程序能拦格式问题，语义问题留给人抽检。"""
    errs = []
    for key in ("instruction", "input", "output"):
        if key not in item or item[key] is None:
            errs.append(f"缺字段:{key}")
    out = item.get("output", "")
    if isinstance(out, str) and len(out) < 4:
        errs.append(f"输出过短({len(out)}字)")
    if any(ph in str(v) for ph in SLOTS for v in item.values()):  # 槽位没填干净
        errs.append("残留未填充槽位")
    return errs


def run_offline():
    data = batch_generate(TEMPLATES, SLOTS)
    print(f"== 批量生成 {len(data)} 条指令数据（Alpaca 风格）==")
    passed = []
    for i, item in enumerate(data, 1):
        errs = quality_check(item)
        tag = "合格" if not errs else "拦截: " + "; ".join(errs)
        print(f"  #{i} [{tag}] {json.dumps(item, ensure_ascii=False)[:70]}")
        if not errs:
            passed.append(item)
    print(f"\n质检结果：{len(passed)}/{len(data)} 条合格入库（不合格已拦截，绝不带病入库）")
    return passed


# ---------------- 真实 LLM 批量段（需 Key，未实跑） ----------------
def run_with_llm(passed):
    """真实流水线：把模板换成 LLM 调用做批量扩写，同样先过 quality_check 再落盘。"""
    try:
        from openai import OpenAI
    except ImportError:
        print("\n[跳过] 未安装 openai（pip install openai），真实 LLM 段略过；离线段已完整演示流水线。")
        return
    if not os.environ.get("OPENAI_API_KEY"):
        print("\n[跳过] 未设置环境变量 OPENAI_API_KEY，真实 LLM 段略过；本课此段未实跑。")
        return
    try:
        client = OpenAI()  # Key 从环境变量读，不硬编码
        model = "gpt-4o-mini"  # 示例名，按官网当前模型列表替换
        extra = client.responses.create(
            model=model,
            input="照这个例子再扩写3条格式相同的客服指令数据：" + json.dumps(passed[0], ensure_ascii=False),
        )
        print("\n== 真实 LLM 扩写结果（需 Key，未实跑，形状示意）==")
        print("  ", extra.output_text[:120])
    except Exception as e:  # 网络/额度/Key 等一律中文提示，不抛裸 traceback
        print(f"\n[失败] 调用 LLM 出错：{type(e).__name__}——请检查 Key、网络与额度。真实段未实跑。")


if __name__ == "__main__":
    passed = run_offline()
    run_with_llm(passed)
