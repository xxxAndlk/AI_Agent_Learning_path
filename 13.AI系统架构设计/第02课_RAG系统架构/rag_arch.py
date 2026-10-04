# rag_arch.py —— RAG 双流水线架构骨架（第13章第02课配套）
# 用途：纯标准库演示「离线建库 + 在线问答」两条流水线的模块边界与数据流
# 运行：python rag_arch.py   零依赖零Key，直接真跑

import time

CHUNK_SIZE = 40  # 每块字符数，调大/调小对比检索效果（讲义想一想③）

DOCS = [
    {"id": "d1", "text": "本公司的年假政策：入职满一年五天，满三年十天，满五年十五天。年假需提前三个工作日在系统申请。",
     "acl": "all"},
    {"id": "d2", "text": "报销流程：先在OA提交发票照片，金额超五千需主管加签，财务每周三集中打款。",
     "acl": "all"},
    {"id": "d3", "text": "薪资带宽属于保密信息，仅限HR与直属主管查阅，不得在任何群聊中讨论。",
     "acl": "hr"},
]


# ============ 离线段：数据接入 → 清洗切分 → 入库 ============
def chunk_text(text):
    chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
    return [c for c in chunks if c.strip()]  # 空白块直接丢弃


def build_index(docs):
    """倒排索引：词 -> [(doc_id, chunk_id)]。真实系统此处是向量库，
    本课用词匹配演示'库'作为两段交接物的角色。"""
    index, chunks = {}, []
    for doc in docs:
        for ci, part in enumerate(chunk_text(doc["text"])):
            cid = len(chunks)
            chunks.append({"doc": doc["id"], "acl": doc["acl"], "text": part})
            for w in set(part):
                index.setdefault(w, []).append(cid)
    print(f"[离线] 接入 {len(docs)} 份文档，切出 {len(chunks)} 块，索引 {len(index)} 个词条")
    return index, chunks


# ============ 在线段：查询处理 → 检索 → 重排 → 生成 ============
def handle_query(q, user_role="all"):
    t0 = time.perf_counter()
    # 查询处理：极简演示——补一个同义变体（真实系统可接LLM改写）
    variants = [q] + ([q.replace("假期", "年假")] if "假期" in q else [])
    # 检索：按角色过滤权限（安全视角），词命中计分海选
    scores = {}
    for v in variants:
        for w in set(v):
            for cid in INDEX.get(w, []):
                if CHUNKS[cid]["acl"] == "all" or CHUNKS[cid]["acl"] == user_role:
                    scores[cid] = scores.get(cid, 0) + 1
    top = sorted(scores, key=scores.get, reverse=True)[:2]
    # 重排：按"包含问句关键词数"再精排一次（延迟换准确）
    def precise(cid):
        return sum(1 for w in set(q) if w in CHUNKS[cid]["text"])
    top.sort(key=precise, reverse=True)
    # 生成：真实系统此处拼提示词调LLM；本课用模板拼装展示数据流
    ctx = "；".join(f"[{CHUNKS[c]['doc']}#{c}] {CHUNKS[c]['text']}" for c in top) or "（无命中）"
    ms = (time.perf_counter() - t0) * 1000
    print(f"[在线] 问：{q}（角色={user_role}）")
    print(f"[在线] 检索→重排命中：{top or '无'}，耗时 {ms:.1f}ms")
    print(f"[在线] 答：依据 {ctx[:60]}…")


if __name__ == "__main__":
    print("=" * 60)
    print("离线段：建库（跑一次，产物供在线段反复读）")
    print("=" * 60)
    INDEX, CHUNKS = build_index(DOCS)
    print()
    print("=" * 60)
    print("在线段：问答（每个请求都走一遍）")
    print("=" * 60)
    handle_query("年假有几天？")
    handle_query("报销流程是什么？")
    handle_query("假期政策")            # 触发查询改写变体
    handle_query("薪资带宽是多少？", user_role="hr")  # 权限过滤视角
