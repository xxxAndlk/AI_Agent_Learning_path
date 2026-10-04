# -*- coding: utf-8 -*-
"""augment_demo.py —— 用纯标准库的小同义词词典做替换增强：
打印增强前后，并演示"乱替换改坏意思"的反例。零第三方依赖，直接真跑。"""

import random

SENTENCES = [
    "我今天很高兴，因为客服服务很好。",
    "这家店价格不高，东西质量很好。",
    "快递今天到了，我很高兴。",
]

# 小同义词词典：key -> 候选写法列表（含原词，抽中原词=本次不替换，模拟"下手轻"）
SYNONYMS = {
    "很好": ["不错", "相当好"],
    "高兴": ["开心", "愉快"],
    "今天": ["今日", "这天"],
}

# 反例专用：不看语境的"危险替换表"，专挑会翻转语义的词
BAD_SYNONYMS = {"高": ["低"], "好": ["差"], "不高": ["极低"]}


def replace_once(text, table, rng):
    """按词典顺序找到第一个命中的词，换成候选之一；找不到返回 None。"""
    for word, cands in table.items():
        idx = text.find(word)
        if idx != -1:
            new = rng.choice(cands)
            return text[:idx] + new + text[idx + len(word):], word, new
    return None


def augment(sents, table, rng, tag):
    print(f"\n== {tag} ==")
    out = []
    for s in sents:
        r = replace_once(s, table, rng)
        if r is None:
            print(f"  (未命中) {s}")
            continue
        new, old, neww = r
        out.append(new)
        mark = "意思不变" if table is SYNONYMS else "!! 意思可能已反转"
        print(f"  原: {s}\n  新: {new}   [{old} -> {neww}] {mark}")
    return out


if __name__ == "__main__":
    rng = random.Random(42)  # 固定随机种子：每次跑结果一致，方便对照
    print("原始句子：")
    for s in SENTENCES:
        print("  ", s)

    good = augment(SENTENCES, SYNONYMS, rng, "正路增强：同义词替换（意思不变）")
    bad = augment(SENTENCES, BAD_SYNONYMS, rng, "反例演示：乱替换（语义被改坏）")

    print("\n== 边界提醒 ==")
    print("  好增强只是换了说法，标签（好评/差评）原样保留；")
    print("  坏增强把'不高''很好'替换反了，句子标签全错——这种数据混进训练集就是毒药。")
    print(f"  实际产出：正路增强 {len(good)} 条可留用，反例 {len(bad)} 条全部作废。")
