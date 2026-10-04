# -*- coding: utf-8 -*-
# 第02课配套程序：FAISS 常用索引怎么选
# 零依赖段：纯标准库模拟 IVF（先分堆、只搜最近几堆）与"跳着找"的先粗后细直觉
# 真实段需安装：pip install faiss-cpu（缺库时打印中文提示并优雅跳过）

import math
import random

random.seed(42)  # 固定随机种子，保证每次运行结果一致


def l2(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def kmeans(points, k, iters=8):
    """迷你 k-means：把点分成 k 堆，返回堆心列表和每点的堆号。"""
    centers = random.sample(points, k)
    for _ in range(iters):
        groups = [[] for _ in range(k)]
        for p in points:
            groups[min(range(k), key=lambda i: l2(p, centers[i]))].append(p)
        centers = [tuple(sum(p[i] for p in g) / len(g) for i in range(len(points[0])))
                   if g else centers[j] for j, g in enumerate(groups)]
    labels = [min(range(k), key=lambda i: l2(p, centers[i])) for p in points]
    return centers, labels


def ivf_search(query, points, labels, centers, nprobe):
    """IVF 直觉：只和 k 个堆心算距离 -> 只进最近的 nprobe 堆 -> 堆内暴力搜。"""
    order = sorted(range(len(centers)), key=lambda i: l2(query, centers[i]))
    visited = order[:nprobe]
    hits = sorted((l2(query, p), p) for p, c in zip(points, labels) if c in visited)
    return hits[:3], visited


def demo_ivf():
    print("=== 零依赖段 1：模拟 IVF（先分堆，只搜最近的几堆） ===")
    points = [(random.uniform(0, 10), random.uniform(0, 10)) for _ in range(20)]
    centers, labels = kmeans(points, 4)
    exact_all = {tuple(q): sorted((l2(q, p), p) for p in points)[:3]
                 for q in [(2, 2), (7, 3), (5, 5)]}
    for q in [(2, 2), (7, 3), (5, 5)]:
        exact = exact_all[tuple(q)]
        line = [f"查询{q}:"]
        for nprobe in (1, 2):
            top3, visited = ivf_search(q, points, labels, centers, nprobe)
            hit = len({p for _, p in top3} & {p for _, p in exact})
            line.append(f"nprobe={nprobe} 只算{len(visited) * 5}条 命中{hit}/3")
        print("  ".join(line))
    print("nprobe=1 时可能漏（最像的在隔壁堆）；多搜 1 堆通常就找回——这就是'旋钮'。")


def demo_hnsw_intuition():
    print("\n=== 零依赖段 2：'跳着找'的先粗后细直觉（HNSW 思路的最简模拟） ===")
    x, pos, path = 37, 0, []
    while pos + 10 <= x:  # 顶层大步跳
        pos += 10
        path.append(pos)
    while pos < x:        # 底层小步走
        pos += 1
        path.append(pos)
    print(f"在一维 0~99 里找 {x}：路径 {path}，共 {len(path)} 步；暴力逐个比要 {x} 步。")
    print("真 HNSW 在高维把'大步/小步'织成多层图：先高速后小路，几步就贴近目标。")


def run_faiss():
    try:
        import faiss
        import numpy as np
        import time
    except ImportError:
        print("[跳过] 未安装 faiss-cpu（pip install faiss-cpu），真实 FAISS 段跳过；零依赖演示已完整跑通。")
        return

    n, d, nlist = 3000, 16, 16
    rs = np.random.RandomState(42)
    xb = rs.rand(n, d).astype("float32")
    xq = rs.rand(20, d).astype("float32")

    flat = faiss.IndexFlatL2(d)
    flat.add(xb)
    _, gt = flat.search(xq, 10)  # 精确答案当标尺

    ivf = faiss.IndexIVFFlat(faiss.IndexFlatL2(d), d, nlist)
    ivf.train(xb)  # IVF 必须先 train 学出堆心，才能 add
    ivf.add(xb)
    print(f"\n=== 真实 FAISS 段：{n} 条 {d} 维，IVF(nlist={nlist}) 对照精确 Flat ===")
    for nprobe in (1, 4, nlist):
        ivf.nprobe = nprobe
        _, I = ivf.search(xq, 10)
        recall = sum(len(set(a) & set(b)) for a, b in zip(I, gt)) / (len(xq) * 10)
        print(f"  nprobe={nprobe:2d}: 召回率 {recall:.0%}")

    hnsw = faiss.IndexHNSWFlat(d, 16)
    hnsw.add(xb)  # HNSW 不用训练，建好就能加
    t0 = time.perf_counter()
    _, I = hnsw.search(xq, 10)
    cost = (time.perf_counter() - t0) / len(xq) * 1000
    recall = sum(len(set(a) & set(b)) for a, b in zip(I, gt)) / (len(xq) * 10)
    print(f"  HNSW      : 召回率 {recall:.0%}，平均每次 {cost:.2f} ms")


if __name__ == "__main__":
    demo_ivf()
    demo_hnsw_intuition()
    run_faiss()
