# -*- coding: utf-8 -*-
"""第04课配套：向量索引算法讲透 —— 纯标准库手算 PQ 压缩/解压/误差 + 各库索引菜单对照。
全程零依赖，无需安装任何库。IVF/HNSW 的搜索模拟第 7 章第 02 课已做过，本课不重复。"""

VEC_DIM = 8   # 原始向量维度（玩具版；真实项目常见 128~1536 维）
SEG = 2       # 切成几段
K = 2         # 每段码本代表数（想一想④：改成 4 再跑，看误差与体积各怎么变）

# 训练数据：前 4 维偏"烹饪"、后 4 维偏"编程"两种风格
TRAIN = [
    [1.0, 0.9, 0.2, 0.1, 0.0, 0.1, 0.0, 0.2],
    [0.8, 1.0, 0.1, 0.3, 0.1, 0.0, 0.2, 0.0],
    [0.1, 0.2, 0.0, 0.1, 0.9, 1.0, 0.8, 0.9],
    [0.0, 0.1, 0.2, 0.0, 1.0, 0.8, 0.9, 1.0],
    [0.9, 0.8, 0.3, 0.2, 0.2, 0.1, 0.1, 0.0],
    [0.2, 0.0, 0.1, 0.2, 0.8, 0.9, 1.0, 0.8],
]


def seg(v, i):
    step = VEC_DIM // SEG
    return v[i * step:(i + 1) * step]


def d2(a, b):
    return sum((x - y) ** 2 for x, y in zip(a, b))


def build_codebook(subs, k):
    """迷你 k-means：均匀取样当起点 -> 分配 -> 均值更新，迭代 3 轮"""
    reps = [list(subs[i * len(subs) // k]) for i in range(k)]
    for _ in range(3):
        groups = [[] for _ in range(k)]
        for s in subs:
            groups[min(range(k), key=lambda r: d2(s, reps[r]))].append(s)
        for j in range(k):
            if groups[j]:
                reps[j] = [sum(col) / len(groups[j]) for col in zip(*groups[j])]
    return reps


def encode(v, books):
    """编码：每段只记'最像的代表是几号'"""
    return [min(range(len(b)), key=lambda r: d2(seg(v, i), b[r])) for i, b in enumerate(books)]


def decode(code, books):
    """解压：代表的拼接 ≈ 原向量（有损）"""
    return [x for i, r in enumerate(code) for x in books[i][r]]


def pq_demo():
    print("=" * 50)
    print(f"[纯标准库] PQ 手算：{VEC_DIM} 维切成 {SEG} 段，每段 {K} 个代表")
    print("=" * 50)
    books = [build_codebook([seg(v, i) for v in TRAIN], K) for i in range(SEG)]
    for i, b in enumerate(books):
        print(f"段{i} 码本(代表向量):", [[round(x, 2) for x in r] for r in b])

    codes = {n: encode(v, books) for n, v in enumerate(TRAIN)}
    print("\n编码结果（每段一个编号）:", codes)

    # 体积账：float32 每数 4 字节；编码后每段 1 字节（真实 PQ 惯例，256 代表恰好 1 字节）
    raw = VEC_DIM * 4
    packed = SEG * 1
    print(f"\n体积账: {VEC_DIM} 维 float32 = {raw} 字节 -> {SEG} 段编号 = {packed} 字节"
          f"，压缩 {raw // packed} 倍（真实 128 维 16 段: 512->16 字节，32 倍）")

    # 重建误差
    errs = [d2(v, decode(codes[n], books)) for n, v in enumerate(TRAIN)]
    print("各向量重建误差(平方和):", [round(e, 3) for e in errs],
          f"平均 {sum(errs) / len(errs):.3f} <- 有损的代价")

    # 近似检索（ADC 查表）：先算查询向量每段到各代表的距离表，再查表求和
    q = [0.9, 1.0, 0.2, 0.1, 0.1, 0.0, 0.1, 0.1]
    tables = [[d2(seg(q, i), rep) for rep in b] for i, b in enumerate(books)]
    approx = sorted((sum(tables[i][codes[n][i]] for i in range(SEG)), n) for n in range(len(TRAIN)))
    exact = sorted((d2(q, v), n) for n, v in enumerate(TRAIN))
    print("\n查询向量近似 Top3(PQ查表):", [(n, round(s, 2)) for s, n in approx[:3]])
    print("查询向量精确 Top3(硬算)  :", [(n, round(s, 2)) for s, n in exact[:3]])
    print("^ 排序可能一致，距离值是'估'的——先 PQ 粗召回收窄范围，再精算排序是常见组合拳")


def menu_demo():
    print()
    print("=" * 50)
    print("[对照] 同一原理，各库的'菜名'（本课不重复模拟 IVF/HNSW 搜索）")
    print("=" * 50)
    rows = [
        ("FAISS",  "IndexFlatL2 / IVF / HNSW / PQ 全家桶", "你自己选（第7章练过）"),
        ("Chroma", "默认 HNSW 系",                        "它替你选"),
        ("Milvus", "IVF_FLAT / IVF_SQ8 / IVF_PQ / HNSW",  "你选，菜单最全"),
        ("pgvector", "ivfflat / hnsw",                    "你选，二选一"),
    ]
    for lib, menu, who in rows:
        print(f"{lib:<9} {menu:<38} {who}")
    print("^ 算法公用，差别只在'给不给你选、替不替你调'；距离度量是另一个独立旋钮")


if __name__ == "__main__":
    pq_demo()
    menu_demo()
    print("\n一句话收束：IVF 省计算、HNSW 省路径、PQ 省存储——三招通用，各库只是上菜方式不同。")
