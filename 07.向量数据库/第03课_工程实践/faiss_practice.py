# -*- coding: utf-8 -*-
# 第03课配套程序：工程实践——增量添加、按ID管理、存盘加载
# 零依赖段：纯标准库实现"向量仓库"（对账表 + 存盘读回；临时文件自动清理）
# 真实段需安装：pip install faiss-cpu（缺库时打印中文提示并优雅跳过）
# 说明：本文件是课程教学演示程序，演示向量库存取，不是工具脚本。

import json
import math
import os
import tempfile

# 业务ID -> (名字, 向量)：甜度、冰量两个维度
DOCS = {
    1001: ("珍珠奶茶", (8.0, 2.0)),
    1002: ("冰美式", (2.0, 9.0)),
    1003: ("热可可", (9.0, 0.0)),
    1004: ("柠檬茶", (5.0, 7.0)),
    1005: ("热牛奶", (4.0, 1.0)),
}
QUERY = (8.0, 1.0)  # 很甜、几乎不加冰


class VectorStore:
    """极简向量仓库：位号列表 + 业务ID对账表，演示'过日子'的增删搜存。"""

    def __init__(self):
        self.vecs = []    # 位号 -> 向量
        self.ids = []     # 位号 -> 业务ID
        self.id2pos = {}  # 业务ID -> 位号（对账表）

    def add(self, vid, vec):
        self.id2pos[vid] = len(self.vecs)
        self.vecs.append(list(vec))
        self.ids.append(vid)

    def remove(self, vid):
        pos = self.id2pos.pop(vid)
        self.vecs.pop(pos)
        self.ids.pop(pos)
        # 关键点：中间删一条，后面位号整体前挪，对账表必须重建！
        self.id2pos = {v: i for i, v in enumerate(self.ids)}

    def nearest(self, query, k=2):
        """最近邻：每条都算一遍距离再排座次（暴力，够教学用）。"""
        ranked = sorted((math.dist(query, v), vid)
                        for vid, v in zip(self.ids, self.vecs))
        return ranked[:k]

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"vecs": self.vecs, "ids": self.ids}, f, ensure_ascii=False)

    @classmethod
    def load(cls, path):
        store = cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        store.vecs, store.ids = data["vecs"], data["ids"]
        store.id2pos = {v: i for i, v in enumerate(store.ids)}
        return store


def demo_offline():
    print("=== 零依赖段：向量仓库（增 / 删 / 搜 / 存盘 / 读回） ===")
    store = VectorStore()
    for vid, (_, vec) in DOCS.items():
        store.add(vid, vec)  # 增量添加：来一条加一条
    top = store.nearest(QUERY)
    print(f"查询{QUERY} Top-2:", [(vid, f"{d:.3f}") for d, vid in top])

    with tempfile.TemporaryDirectory() as td:  # 临时目录，跑完自动清理
        path = os.path.join(td, "store.json")
        store.save(path)                       # 存盘
        back = VectorStore.load(path)          # 读回
        print("存盘读回后 Top-2 一致:", back.nearest(QUERY) == top)

        print("删除前对账表:", store.id2pos)
        store.remove(1001)
        print("删除 1001 后:", store.id2pos, "<- 位号整体前挪，对账表重建")
        print("再查 Top-2:", [(vid, f"{d:.3f}") for d, vid in store.nearest(QUERY)])


def run_faiss():
    try:
        import faiss
        import numpy as np
    except ImportError:
        print("[跳过] 未安装 faiss-cpu（pip install faiss-cpu），真实 FAISS 段跳过；零依赖演示已完整跑通。")
        return

    print("\n=== 真实 FAISS 段：IndexIDMap 按业务ID增删 + 存盘加载 ===")
    ids = np.array(list(DOCS.keys()), dtype="int64")
    xb = np.array([vec for _, vec in DOCS.values()], dtype="float32")
    index = faiss.IndexIDMap(faiss.IndexFlatL2(xb.shape[1]))
    index.add_with_ids(xb, ids)  # 直接存业务ID
    q = np.array([QUERY], dtype="float32")
    D, I = index.search(q, 2)
    print("直接返回业务ID:", list(zip(I[0].tolist(), D[0].tolist())))

    index.remove_ids(np.array([1001], dtype="int64"))
    D, I = index.search(q, 2)
    print("删除 1001 后:", list(zip(I[0].tolist(), D[0].tolist())))

    with tempfile.TemporaryDirectory() as td:
        path = os.path.join(td, "demo.faiss")
        faiss.write_index(index, path)   # 存盘
        back = faiss.read_index(path)    # 读回
        D, I = back.search(q, 2)
        print("存盘读回后:", list(zip(I[0].tolist(), D[0].tolist())))
        print(f"向量数 {index.ntotal} -> 读回 {back.ntotal}，数据与结构完整复活。")


if __name__ == "__main__":
    demo_offline()
    run_faiss()
