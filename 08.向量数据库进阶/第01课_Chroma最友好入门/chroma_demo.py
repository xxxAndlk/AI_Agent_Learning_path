# -*- coding: utf-8 -*-
"""第01课配套：Chroma 最友好入门 —— 先用纯标准库造一个迷你向量库，再体验真实 Chroma。
真实库安装: pip install chromadb（未安装时真实段中文提示跳过，纯标准库段照常运行）
演示直接传向量（离线可跑）；真实项目不传向量时 Chroma 会自动嵌入（首次需下载模型）。"""

import json
import math
import os
import tempfile


# ---------- 第一部分：纯标准库迷你 Chroma ----------
def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


class MiniVectorDB:
    """迷你 Chroma：集合 -> 文档(文本/向量/元数据)，支持增删改查+元数据过滤+持久化"""

    def __init__(self, path=None):
        self.path = path
        self.collections = {}
        if path and os.path.exists(path):  # PersistentClient 的灵魂：重启读回
            with open(path, encoding="utf-8") as f:
                self.collections = json.load(f)

    def get_or_create_collection(self, name):
        return self.collections.setdefault(name, {})

    def add(self, col, doc_id, text, vec, metadata=None):
        col[doc_id] = {"text": text, "vec": vec, "meta": metadata or {}}

    def update(self, col, doc_id, text):
        if doc_id in col:
            col[doc_id]["text"] = text

    def delete(self, col, doc_id):
        col.pop(doc_id, None)

    @staticmethod
    def _match(meta, where):
        return all(meta.get(k) == v for k, v in where.items())

    def query(self, col, qvec, n=2, where=None):
        pool = [(i, d) for i, d in col.items() if not where or self._match(d["meta"], where)]
        pool.sort(key=lambda p: -cosine(qvec, p[1]["vec"]))
        return [(i, d["text"], round(cosine(qvec, d["vec"]), 3)) for i, d in pool[:n]]

    def save(self):
        if self.path:
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump(self.collections, f, ensure_ascii=False)


def mini_demo():
    print("=" * 46)
    print("[纯标准库] 迷你 Chroma：集合/CRUD/过滤/持久化")
    print("=" * 46)
    db = MiniVectorDB(os.path.join(tempfile.mkdtemp(prefix="mini_chroma_"), "db.json"))
    col = db.get_or_create_collection("recipes")
    docs = [("1", "红烧肉要先焯水再小火炖", {"category": "美食"}, [1, 1, 0]),
            ("2", "Python 列表推导式写起来最爽", {"category": "编程"}, [0, 0, 1]),
            ("3", "清蒸鱼讲究火候与鲜度", {"category": "美食"}, [0.9, 1, 0.1])]
    for i, t, m, v in docs:  # 手工小向量：前两维=烹饪倾向，第三维=编程倾向
        db.add(col, i, t, v, m)
    print("已入库:", len(col), "条")
    print("不过滤搜'怎么炖肉'  :", db.query(col, [1, 1, 0.2]))
    print("where 只看美食类    :", db.query(col, [1, 1, 0.2], where={"category": "美食"}))
    db.update(col, "1", "红烧肉焯水后要炖足九十分钟")
    db.delete(col, "3")
    print("改1删3后剩:", len(col), "条")
    db.save()
    db2 = MiniVectorDB(db.path)  # 模拟重启
    back = db2.get_or_create_collection("recipes")
    print("重启后读回:", len(back), "条 -> 数据不再随程序蒸发")


# ---------- 第二部分：真实 Chroma（需 pip install chromadb）----------
def real_demo():
    print()
    print("=" * 46)
    print("[真实库] Chroma PersistentClient")
    print("=" * 46)
    try:
        import chromadb
    except ImportError:
        print("未安装 chromadb，本段跳过。安装: pip install chromadb")
        return
    try:
        client = chromadb.PersistentClient(path=os.path.join(tempfile.mkdtemp(prefix="chroma_"), "db"))
        col = client.get_or_create_collection("recipes")
        col.add(ids=["1", "2"],
                documents=["红烧肉要先焯水再小火炖", "Python 列表推导式写起来最爽"],
                metadatas=[{"category": "美食"}, {"category": "编程"}],
                embeddings=[[1, 1, 0], [0, 0, 1]])  # 传向量=离线可跑；不传则自动嵌入
        res = col.query(query_embeddings=[[1, 1, 0.2]], n_results=2,
                        where={"category": "美食"})
        print("query(美食过滤)命中:", res["documents"][0])
        col.update(ids=["1"], documents=["红烧肉焯水后要炖足九十分钟"])
        print("update 后 count =", col.count())
        col.delete(ids=["2"])
        print("delete 后 count =", col.count())
    except Exception as e:  # 版本差异/环境问题都不裸抛
        print("Chroma 段运行异常，已跳过:", type(e).__name__, "-", str(e)[:60])


if __name__ == "__main__":
    mini_demo()
    real_demo()
    print("\n一句话收束：集合+文档+元数据+持久化，数据库的核心骨架就这么点——真实 Chroma 只是把它做得更稳更快。")
