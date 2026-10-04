# -*- coding: utf-8 -*-
"""第03课配套：PGVector —— 同一需求走两条路：看等价 SQL + 零 SQL 封装；再连真实 PostgreSQL。
真实段安装: pip install "psycopg[binary]" pgvector（还需本机装 PostgreSQL）
连接串从环境变量 PG_DSN 读，示例: postgresql://postgres:密码@localhost:5432/postgres"""

import math
import os

# 一张"菜谱表"：向量故意用 3 维便于演示，真实项目常见 768/1536 维
ROWS = [
    {"id": 1, "content": "红烧肉先焯水再小火炖", "price": 45, "embedding": [1, 1, 0]},
    {"id": 2, "content": "Python 列表推导式写法", "price": 0, "embedding": [0, 0, 1]},
    {"id": 3, "content": "清蒸鱼讲究火候", "price": 60, "embedding": [0.9, 1, 0.1]},
    {"id": 4, "content": " budget 红烧茄子做法", "price": 20, "embedding": [0.8, 0.9, 0.2]},
]


def cosine_dist(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return 1 - dot / (na * nb) if na and nb else 1.0  # 距离越小越像，对应 SQL 的 <=>


# ---------- 第一部分：纯标准库，一条需求两条走法 ----------
class FakePG:
    """模拟 PostgreSQL 表；每个方法打印等价 SQL，封装本身不写一行 SQL"""

    def __init__(self):
        self.table = [dict(r) for r in ROWS]

    def create_table(self):
        print("封装 create_table() 等价于:\n"
              "  CREATE TABLE dishes (id serial PRIMARY KEY, content text,\n"
              "                       price numeric, embedding vector(3));")

    def search(self, qvec, price_max=None, keyword=None, top=2):
        sql = ["SELECT content, price FROM dishes WHERE TRUE"]
        if price_max is not None:
            sql.append(f"  AND price <= {price_max}")
        if keyword:
            sql.append(f"  AND content ILIKE '%{keyword}%'")
        sql.append(f"  ORDER BY embedding <=> :查询向量 LIMIT {top}")
        print("封装 search() 等价于:\n  " + "\n  ".join(sql))
        rows = self.table
        if price_max is not None:  # 结构化过滤
            rows = [r for r in rows if r["price"] <= price_max]
        if keyword:  # ILIKE：不区分大小写的"包含"
            rows = [r for r in rows if keyword.lower() in r["content"].lower()]
        rows = sorted(rows, key=lambda r: cosine_dist(qvec, r["embedding"]))
        return rows[:top]


def zero_sql_demo():
    print("=" * 46)
    print("[纯标准库] 一张表 + 结构化过滤 + 向量排序")
    print("=" * 46)
    pg = FakePG()
    pg.create_table()
    print("\n-- 需求：50 元以内、和'怎么炖肉'最像的菜 --")
    for r in pg.search([1, 1, 0.2], price_max=50):
        print("  命中:", r["content"], "| 价格:", r["price"])
    print("\n-- 需求：含'红烧'、最像的 1 条（ILIKE 模糊匹配）--")
    for r in pg.search([1, 1, 0.2], keyword="红烧", top=1):
        print("  命中:", r["content"])
    print("↑ 全程零 SQL：建表/过滤/排序全被封装藏好，你只需'看得懂'等价 SQL")


# ---------- 第二部分：真实 PostgreSQL + PGVector ----------
def real_demo():
    print()
    print("=" * 46)
    print("[真实库] psycopg 连 PostgreSQL（需本机服务 + PG_DSN 环境变量）")
    print("=" * 46)
    dsn = os.environ.get("PG_DSN")
    if not dsn:
        print("未设置 PG_DSN，本段跳过。示例: postgresql://postgres:密码@localhost:5432/postgres")
        return
    try:
        import psycopg
    except ImportError:
        print('未安装 psycopg，本段跳过。安装: pip install "psycopg[binary]" pgvector')
        return
    try:
        with psycopg.connect(dsn) as conn:
            conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            conn.execute("""CREATE TABLE IF NOT EXISTS dishes (
                id serial PRIMARY KEY, content text,
                price numeric, embedding vector(3))""")
            conn.execute("DELETE FROM dishes")
            for r in ROWS:  # %s 占位防注入；向量以字符串传入自动转型
                conn.execute(
                    "INSERT INTO dishes (content, price, embedding) VALUES (%s, %s, %s)",
                    (r["content"], r["price"], "[" + ",".join(str(x) for x in r["embedding"]) + "]"))
            cur = conn.execute(
                """SELECT content, price FROM dishes
                   WHERE price <= %s ORDER BY embedding <=> %s::vector LIMIT 2""",
                (50, "[1,1,0.2]"))
            for content, price in cur.fetchall():
                print("  真库命中:", content, "| 价格:", price)
    except Exception as e:
        print("连接/执行失败，本段跳过:", type(e).__name__, "-", str(e)[:60])


if __name__ == "__main__":
    zero_sql_demo()
    real_demo()
    print("\n一句话收束：老数据库装新插件，业务数据和向量同库同事务——'混合查询'在这里是一句 SQL 的事。")
