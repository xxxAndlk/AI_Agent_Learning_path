# -*- coding: utf-8 -*-
# 用途：离线演示两阶段检索——先用"向量粗筛"海选，再用"精排"细读重排，看清排序如何被纠正。
# 运行：python rerank_demo.py （纯标准库，无需安装任何包，可离线直接运行）
# 说明：末尾 real_reranker_demo 是"真实 reranker 服务"调用示例，需自备 API Key
#       （环境变量 RERANK_API_KEY），本段未实跑；离线部分已完整覆盖两阶段排序的核心逻辑。
import math
import sys

# Windows 控制台默认 GBK，把输出流切到 UTF-8 防中文乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

QUESTION = "我们的大模型服务总是过热，该怎么给它降温？"

# 5 条候选。注意 [E]：字面和问题高度相似（都带"温度/调低"），其实在讲输出随机度——
# 这正是双塔最容易放进 top 的"词面像、答非所问"片段
CANDIDATES = {
    "A": "训练大模型时学习率过高容易导致损失震荡，可以先调低学习率再逐步回升。",
    "B": "大模型推理显存吃紧？试试量化（INT8/INT4）与 KV 缓存量化，能明显降低显存占用。",
    "C": "机房空调设定在 22-26 摄氏度，配合热通道封闭，是服务器散热的基础做法。",
    "D": "给推理服务降温的常见思路：限制并发与批大小、启用低功耗推理框架、必要时升级散热。",
    "E": "把模型的温度（temperature）参数调低，输出会更稳定、更少胡言乱语。",
}

# ---------- 第一阶段：模拟"双塔粗筛" ----------
# 手工小向量，3 维大致代表：[物理降温/散热, 模型服务/推理, 字面出现"温度"类词]
# 真实系统里是嵌入模型算出的上千维向量，这里压成 3 维方便肉眼看规律
VECTORS = {
    "Q": [0.6, 0.5, 0.5],    # 问题：主体是物理降温，字面也带"过热"
    "A": [0.0, 0.9, 0.1],
    "B": [0.2, 0.8, 0.1],
    "C": [0.9, 0.3, 0.1],
    "D": [0.85, 0.7, 0.05],
    "E": [0.05, 0.6, 0.95],  # "温度参数"在字面维度爆表——双塔的盲区就出在这
}


def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(x * x for x in b))
    return dot / (na * nb) if na and nb else 0.0


def coarse_rank(top_n):
    """双塔：问题与候选各自编码成向量、只比整体距离——快，但看不清词与词的细节"""
    scored = sorted(
        ((cid, cosine(VECTORS["Q"], vec)) for cid, vec in VECTORS.items() if cid != "Q"),
        key=lambda t: t[1], reverse=True)
    return scored[:top_n]


# ---------- 第二阶段：模拟"交叉精排" ----------
# 真实 Cross-Encoder 把「问题 + 候选」拼在一起送进模型细读打分；
# 这里用最朴素的近似：数候选文本的主题词命中数，再用陷阱词识破"字面像、答非所问"
TOPIC_WORDS = ["降温", "散热", "过热", "空调", "风扇", "机房"]
TRAP_MARKS = ("temperature", "参数")  # 两者同时出现 = 在讲输出随机度，狠狠扣分


def fine_score(text):
    score = sum(text.count(w) for w in TOPIC_WORDS)
    if all(m in text for m in TRAP_MARKS):
        score -= 3
    return score


def main():
    print("=" * 60)
    print(f"问题：{QUESTION}")
    print("=" * 60)

    print("\n【第一阶段 · 粗筛】双塔各自编码、比距离 —— 取 Top 3（求不漏）")
    coarse = coarse_rank(top_n=3)
    for i, (cid, s) in enumerate(coarse, 1):
        print(f"  {i}. [{cid}] 粗筛分 {s:.3f}  {CANDIDATES[cid]}")

    print("\n【第二阶段 · 精排】问题+候选拼一起细读打分 —— 只看粗筛 Top 3（求准）")
    reranked = sorted(((cid, fine_score(CANDIDATES[cid])) for cid, _ in coarse),
                      key=lambda t: t[1], reverse=True)
    for i, (cid, s) in enumerate(reranked, 1):
        print(f"  {i}. [{cid}] 精排分 {s:+d}  {CANDIDATES[cid]}")

    before = [cid for cid, _ in coarse]
    after = [cid for cid, _ in reranked]
    print(f"\n粗筛顺序：{' > '.join(before)}")
    print(f"精排顺序：{' > '.join(after)}")
    if before != after:
        print("排序变了——精排把词面像、答非所问的候选摁了下去（对比上面两行看谁升谁降）")
    top2 = after[:2]
    print(f"最终取 Top 2 交给大模型生成：{top2}（答非所问的候选进不了上下文）")

    real_reranker_demo()


def real_reranker_demo():
    """真实 reranker 服务调用示例（需 API Key，未实跑）。
    上面两个函数是教学近似；生产中精排这步交给专门的 reranker：
    本地起 BGE reranker，或调商用 rerank API（下面以一个通用端点为例）。"""
    import http.client
    import json
    import os

    api_key = os.environ.get("RERANK_API_KEY")
    if not api_key:
        print("\n[跳过] 未检测到环境变量 RERANK_API_KEY，真实 reranker 段未运行（离线演示已完整）。")
        return

    payload = json.dumps({
        "model": "BAAI/bge-reranker-v2-m3",  # 示例型号，可能已更新，按服务商模型列表选
        "query": QUESTION,
        "documents": [CANDIDATES[cid] for cid in sorted(CANDIDATES)],
        "top_n": 2,
    }).encode("utf-8")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        conn = http.client.HTTPSConnection("api.siliconflow.cn", timeout=15)  # 示例服务商，换成你所用 rerank 服务的域名
        try:
            conn.request("POST", "/v1/rerank", body=payload, headers=headers)  # 路径以服务商文档为准
            resp = conn.getresponse()
            status, body = resp.status, resp.read().decode("utf-8")
        finally:
            conn.close()
        if status != 200:
            print(f"\n[失败] 服务返回状态码 {status}：请检查 Key 是否有效、模型名是否正确、额度是否用尽。")
            return
        data = json.loads(body)
        print("\n【真实 reranker 返回】按相关性从高到低（响应字段以服务商文档为准）：")
        ids = sorted(CANDIDATES)
        for r in data.get("results", []):
            cid = ids[r["index"]]
            print(f"  [{cid}] score={r['relevance_score']:.4f}  {CANDIDATES[cid]}")
    except TimeoutError:
        print("\n[失败] 请求超时：请检查网络或代理后重试。")
    except OSError as e:
        print(f"\n[失败] 网络不通（{e.__class__.__name__}）：请检查网络、域名与代理后重试。")
    except json.JSONDecodeError:
        print("\n[失败] 返回内容不是合法 JSON：请核对端点与参数。")


if __name__ == "__main__":
    main()
