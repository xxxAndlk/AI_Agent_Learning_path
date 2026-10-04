# -*- coding: utf-8 -*-
"""第02课配套：Milvus 为大规模而生 —— Schema 先行/分区/load 三大规矩 + 真实 Milvus Lite。
真实库安装: pip install pymilvus（未安装时真实段中文提示跳过）
Milvus Lite 是嵌入式形态：一个本地文件就是服务，无需部署。"""

import math
import os
import tempfile


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


# ---------- 第一部分：纯标准库，体验服务化数据库的"规矩" ----------
class MiniMilvus:
    """和 Chroma 同样能搜，但多了三样服务化特质：先图纸、分仓、load 后才能搜"""

    def __init__(self):
        self.schema = None
        self.partitions = {}
        self.loaded = False

    def create_collection(self, schema):
        self.schema = schema  # 例: ["id", "text", "category", "embedding"]

    def create_partition(self, name):
        self.partitions.setdefault(name, {})

    def insert(self, partition, row):
        if self.schema is None:
            raise RuntimeError("Schema 未定义：Milvus 先画图纸再收数据")
        missing = [f for f in self.schema if f not in row]
        if missing:
            raise ValueError(f"字段 {missing} 不符合 Schema，拒收")
        self.partitions[partition][row["id"]] = row

    def load(self):
        self.loaded = True  # 数据入库 != 上架：载入内存后才能搜

    def search(self, qvec, partition=None, n=2):
        if not self.loaded:
            raise RuntimeError("先 load() 再 search：Milvus 的数据要载入内存才可搜")
        pools = [partition] if partition else list(self.partitions)
        rows = [r for p in pools for r in self.partitions[p].values()]
        rows.sort(key=lambda r: -cosine(qvec, r["vec"]))
        return [(r["id"], r["text"]) for r in rows[:n]]


def mini_demo():
    print("=" * 46)
    print("[纯标准库] 迷你 Milvus：Schema/分区/load 三大规矩")
    print("=" * 46)
    m = MiniMilvus()
    try:
        m.insert("美食", {"id": 1, "text": "x", "vec": [1, 0]})
    except RuntimeError as e:
        print("规矩① 未建集合就插入 ->", e)
    m.create_collection(["id", "text", "category", "vec"])
    m.create_partition("美食")
    m.create_partition("编程")
    data = [(1, "红烧肉先焯水再炖", "美食", [1, 1, 0]),
            (2, "列表推导式最爽", "编程", [0, 0, 1]),
            (3, "清蒸鱼讲究火候", "美食", [0.9, 1, 0.1])]
    for i, t, c, v in data:
        m.insert(c, {"id": i, "text": t, "category": c, "vec": v})
    print("已按分区入库: 美食", len(m.partitions["美食"]), "条 / 编程", len(m.partitions["编程"]), "条")
    try:
        m.search([1, 1, 0])
    except RuntimeError as e:
        print("规矩② 未 load 就搜 ->", e)
    m.load()
    print("全库搜:", m.search([1, 1, 0]))
    print("只搜'美食'分区:", m.search([1, 1, 0], partition="美食"), "<- 搜索范围直接砍半")


# ---------- 第二部分：真实 Milvus Lite（需 pip install pymilvus）----------
def real_demo():
    print()
    print("=" * 46)
    print("[真实库] Milvus Lite（本地文件即服务）")
    print("=" * 46)
    try:
        from pymilvus import DataType, MilvusClient
    except ImportError:
        print("未安装 pymilvus，本段跳过。安装: pip install pymilvus")
        return
    try:
        uri = os.path.join(tempfile.mkdtemp(prefix="milvus_lite_"), "demo.db")
        client = MilvusClient(uri=uri)
        schema = client.create_schema(auto_id=False)
        schema.add_field("id", DataType.INT64, is_primary=True)
        schema.add_field("text", DataType.VARCHAR, max_length=128)
        schema.add_field("category", DataType.VARCHAR, max_length=32)
        schema.add_field("embedding", DataType.FLOAT_VECTOR, dim=3)
        index_params = client.prepare_index_params()
        index_params.add_index(field_name="embedding", index_type="FLAT", metric_type="COSINE")
        client.create_collection("recipes", schema=schema, index_params=index_params)
        client.insert("recipes", [
            {"id": 1, "text": "红烧肉先焯水再炖", "category": "美食", "embedding": [1, 1, 0]},
            {"id": 2, "text": "列表推导式最爽", "category": "编程", "embedding": [0, 0, 1]},
        ])
        client.load_collection("recipes")  # 入库 != 上架，搜之前要 load
        res = client.search(collection_name="recipes", data=[[1, 1, 0.2]], limit=2,
                            filter='category == "美食"', output_fields=["text"])
        print("search(美食过滤)命中:", [hit["entity"]["text"] for hit in res[0]])
    except Exception as e:
        print("Milvus 段运行异常，已跳过:", type(e).__name__, "-", str(e)[:60])


if __name__ == "__main__":
    mini_demo()
    real_demo()
    print("\n一句话收束：Schema 保数据不乱、分区保查询少扫、load 保内存可控——这三条规矩换来的，是并发、副本与水平扩展。")
