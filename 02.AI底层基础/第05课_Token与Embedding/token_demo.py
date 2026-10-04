# -*- coding: utf-8 -*-
"""第05课轻量演示：亲手把文字"切"成 token，再看"相近的词、相近的向量"。

纯标准库，直接运行：python token_demo.py（无需 pip install 任何第三方库）。
想看真实大模型的分词效果，见文件末尾注释（需要额外装库，本课不要求）。
"""
import math

WORDS = ["人工智能", "工人", "人工费", "智能锁", "智力"]


def count_pairs(splits):
    # 统计语料里每对相邻块出现了几次——BPE 的"数一数"就在这
    counts = {}
    for parts in splits:
        for a, b in zip(parts, parts[1:]):
            counts[(a, b)] = counts.get((a, b), 0) + 1
    return counts


def merge_pair(splits, pair):
    # 把整条语料里出现的这对相邻块统统粘成一块
    a, b = pair
    token = a + b
    merged = []
    for parts in splits:
        row, i = [], 0
        while i < len(parts):
            if i + 1 < len(parts) and parts[i] == a and parts[i + 1] == b:
                row.append(token)
                i += 2
            else:
                row.append(parts[i])
                i += 1
        merged.append(row)
    return merged, token


def demo_bpe():
    splits = [list(w) for w in WORDS]
    print("== 第一幕：手写迷你 BPE，看 token 怎么被\"粘\"出来 ==")
    print("语料:", "、".join(WORDS))
    print("第0轮(全拆成单字):", " | ".join("|".join(p) for p in splits))
    learned = []
    for rnd in range(1, 4):
        counts = count_pairs(splits)
        # dict 记住了插入顺序：并列最高频时取先出现的那对，保证每次运行结果一致
        (a, b), freq = max(counts.items(), key=lambda kv: kv[1])
        if freq < 2:
            print(f"第{rnd}轮: 剩下的相邻对都只出现{freq}次，粘了也不划算，收工。")
            break
        splits, token = merge_pair(splits, (a, b))
        learned.append(token)
        print(f"第{rnd}轮: 最常挨在一起的是\"{a}\"+\"{b}\"(出现{freq}次) -> 粘成\"{token}\"")
        print("       现在的切分:", " | ".join("|".join(p) for p in splits))
    print("BPE 学到的新块:", "、".join(learned))
    print("以后遇到含这些块的新词，就能用现成零件拼出来。")


# 手工编的 6 维向量。可以先理解成 6 个"语义刻度"：
# [可爱度, 凶猛度, 体型, 会动, 是食物, 甜度]
# 真实模型里每一维的含义是训练学出来的，没人起名字，这里标刻度只为看得懂。
VECTORS = {
    "猫":   [0.9, 0.1, 0.3, 0.8, 0.0, 0.1],
    "狗":   [0.8, 0.3, 0.4, 0.9, 0.0, 0.1],
    "汽车": [0.0, 0.7, 0.9, 0.8, 0.0, 0.0],
    "苹果": [0.6, 0.0, 0.3, 0.0, 0.9, 0.8],
}


def dot(u, v):
    return sum(a * b for a, b in zip(u, v))


def cosine(u, v):
    # 夹角余弦：只看方向，不看箭头长短，1=同向 0=垂直
    return dot(u, v) / math.sqrt(dot(u, u) * dot(v, v))


def demo_embedding():
    print("\n== 第二幕：相近的词，向量也相近 ==")
    for w, v in VECTORS.items():
        print(f"  {w}: {v}")
    print("以\"猫\"为基准，两两比一比（点积 / 余弦相似度）:")
    for w in ["狗", "汽车", "苹果"]:
        print(f"  猫 vs {w}: dot={dot(VECTORS['猫'], VECTORS[w]):.2f}, "
              f"cos={cosine(VECTORS['猫'], VECTORS[w]):.2f}")
    print("结论: 猫和狗方向最接近，和汽车、苹果明显疏远——数字能表达\"意思近不近\"。")
    print("真实模型里这张表是几千维、几万行，数字全是训练调出来的。")


if __name__ == "__main__":
    demo_bpe()
    demo_embedding()

# ---- 选看：真实大模型的 tokenizer（本课不要求，需要装第三方库）----
# pip install transformers
# from transformers import AutoTokenizer
# tok = AutoTokenizer.from_pretrained("Qwen/Qwen2.5-7B-Instruct")  # 也可换成你手边的模型
# print(tok.tokenize("文字怎么变成数字"))  # 看看真实模型把这句话切成哪几块
