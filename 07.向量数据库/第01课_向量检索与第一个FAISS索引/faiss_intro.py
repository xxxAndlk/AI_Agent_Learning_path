# -*- coding: utf-8 -*-
# 第01课配套程序：向量检索与第一个 FAISS 索引
# 零依赖段：纯标准库手写"暴力最近邻"，无任何第三方库即可真跑
# 真实段需安装：pip install faiss-cpu（缺库时打印中文提示并优雅跳过）

import math
import time

# 每杯饮品用两个维度描述：甜度(0~10)、冰量(0~10)
DRINKS = [
    ("珍珠奶茶", 8, 2),
    ("冰美式", 2, 9),
    ("热可可", 9, 0),
    ("柠檬茶", 5, 7),
    ("双倍糖冰奶茶", 16, 2),  # 方向与查询一致、量级翻倍，教学彩蛋
]
QUERY = (8.0, 1.0)  # 我想喝：很甜、几乎不加冰


def l2(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb)


def brute_force(query, items, score, topk=3, higher_better=True):
    """暴力搜索：每条都算一遍再排座次——这也是 FAISS Flat 索引的本质。"""
    ranked = sorted(((score(query, vec), name) for name, *vec in items),
                    key=lambda t: t[0], reverse=higher_better)
    return ranked[:topk]


def demo_offline():
    print("=== 零依赖段：手写暴力最近邻（零依赖，纯标准库） ===")
    print(f"查询：甜度 {QUERY[0]}、冰量 {QUERY[1]}（很甜、几乎不加冰）")
    print("\n按 L2 距离（越小越像）：")
    for rank, (d, name) in enumerate(brute_force(QUERY, DRINKS, l2), 1):
        print(f"  {rank}. {name}  L2={d:.3f}")
    print("\n按 余弦相似度（越大越像）：")
    for rank, (s, name) in enumerate(brute_force(QUERY, DRINKS, cosine), 1):
        print(f"  {rank}. {name}  cos={s:.3f}")
    print("\n两把尺子冠军不同：L2 只认'数值接近'，余弦只认'方向一致'——")
    print("'双倍糖冰奶茶'方向和查询完全一致（余弦封顶），但量级翻倍（L2 很远）。")


def run_faiss():
    try:
        import faiss
        import numpy as np
    except ImportError:
        print("[跳过] 未安装 faiss-cpu（pip install faiss-cpu），真实 FAISS 段跳过；零依赖演示已完整跑通。")
        return

    print("\n=== 真实 FAISS 段：IndexFlatL2 ===")
    xb = np.array([vec for _, *vec in DRINKS], dtype="float32")  # 必须转 float32！
    index = faiss.IndexFlatL2(xb.shape[1])
    index.add(xb)
    D, I = index.search(np.array([QUERY], dtype="float32"), 3)
    print("FAISS Flat 的 Top-3（I 是位号，按 add 顺序从 0 编号）：")
    for pos, dist in zip(I[0], D[0]):
        print(f"  位号 {pos} -> {DRINKS[pos][0]}  L2={dist:.3f}")

    n, dim = 20000, 16
    rs = np.random.RandomState(42)
    big_index = faiss.IndexFlatL2(dim)
    big_index.add(rs.rand(n, dim).astype("float32"))
    qs = rs.rand(50, dim).astype("float32")
    t0 = time.perf_counter()
    big_index.search(qs, 5)
    cost = (time.perf_counter() - t0) / len(qs) * 1000
    print(f"\n{n} 条 {dim} 维向量，Flat 精确搜 1 次约 {cost:.2f} ms（C++ 内核的小宇宙）。")
    print("数据再翻 100 倍呢？这就该请出下一课的 IVF / HNSW / PQ 了。")


if __name__ == "__main__":
    demo_offline()
    run_faiss()
