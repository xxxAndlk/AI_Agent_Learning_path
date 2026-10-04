# -*- coding: utf-8 -*-
"""mini_rag.py —— 最小 RAG 流水线：离线"切块→入库→检索→拼提示"纯标准库真跑，最后一步调模型生成需 API Key。

运行离线部分（零依赖）：python mini_rag.py
生成部分为可选项：需联网与 Key，未配置时中文提示并优雅跳过，不会报错也不会伪造输出
    pip install openai python-dotenv
"""
import math
import os
import re

# ---------- 1. 写死的几条中文文档。来源名就是元数据：真实系统里是文件名/网址/页码 ----------
DOCS = [
    ("报销制度.md", "差旅报销需要在出差结束后10天内提交发票。发票抬头必须与公司名称一致，否则财务会退回。"),
    ("考勤制度.md", "请假一天以内由直属主管审批，超过三天需要部门总监签字。迟到三次按旷工半天处理。"),
    ("电脑与账号.md", "登录密码每90天必须更换一次，不能与最近三次用过的密码重复。公司电脑丢失要第一时间联系IT挂失。"),
    ("团建与活动.md", "每季度有一次团队建设活动，费用由部门经费承担。团建当天不安排加班。"),
]

# ---------- 2. 切块：按句末标点切开，一句一块（第02课切块思想的极简版） ----------
def split_chunks(text):
    return [s for s in re.split(r"(?<=[。！？])", text) if s.strip()]

# ---------- 3. 手工嵌入：词袋向量。真实系统换成嵌入模型，但两处必须用同一套 ----------
KEYWORDS = ["报销", "发票", "请假", "审批", "密码", "团建"]

def embed(text):
    """把一段文字变成 6 维向量：每个维度 = 对应关键词出现的次数。"""
    return [text.count(k) for k in KEYWORDS]

def cosine(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    return dot / (na * nb) if na and nb else 0.0

# ---------- 4. 离线建库：向量 + 原文 + 元数据 三样一起存（内存版向量库） ----------
store = []
for source, text in DOCS:
    for i, chunk in enumerate(split_chunks(text), 1):
        store.append({"vector": embed(chunk), "text": chunk, "source": source, "chunk": i})

print("=" * 62)
print(f"[1] 离线建库完成：4 份文档共切成 {len(store)} 个块")
for item in store:
    print(f"    [{item['source']} #{item['chunk']}] {item['text']}")
print("    向量示例（维度顺序 [报销, 发票, 请假, 审批, 密码, 团建]）：")
print(f"    {store[0]['text']} -> {store[0]['vector']}")

# ---------- 5. 在线问答：问题用同一个 embed 函数（换模型等于换坐标系，距离就没意义了） ----------
QUESTION = "出差回来多久之内要提交报销？"
q_vec = embed(QUESTION)

TOP_K, MIN_SCORE = 2, 0.05  # k=2 取前两块；分数低于 0.05 视为不相关，丢弃
scored = sorted(
    ((cosine(q_vec, it["vector"]), it) for it in store),
    key=lambda pair: pair[0], reverse=True,
)
print("=" * 62)
print(f"[2] 问题：{QUESTION}")
print(f"    问题向量 -> {q_vec}")
for score, it in scored:
    verdict = "命中" if score >= MIN_SCORE else "低于阈值，丢弃"
    print(f"    相似度 {score:.3f}  {verdict}  [{it['source']} #{it['chunk']}]")
hits = [it for score, it in scored[:TOP_K] if score >= MIN_SCORE]

# ---------- 6. 拼提示：片段编号 + 来源 + "只依据资料"的纪律句 ----------
context = "\n".join(f"[{n}] （来源：{it['source']}）{it['text']}" for n, it in enumerate(hits, 1))
prompt = (
    "请只依据下面的资料回答问题；资料不足以回答时，直接说\"资料里没有\"，不要猜。\n"
    "回答末尾用 [编号] 注明用了哪几条资料。\n\n"
    f"资料：\n{context}\n\n问题：{QUESTION}"
)
print("=" * 62)
print("[3] 拼好的最终提示：")
print(prompt)
print("=" * 62)

# ---------- 7. 生成：需 API Key 与 openai 库，缺任一项优雅跳过 ----------
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("[4] 生成阶段跳过：未设置环境变量 OPENAI_API_KEY。")
    print("    配置 Key 并 pip install openai python-dotenv 后，模型会基于上面的提示生成带出处的回答。")
else:
    try:
        from openai import OpenAI
    except ImportError:
        print("[4] 生成阶段跳过：已检测到 Key，但未安装 openai 库（pip install openai python-dotenv）。")
    else:
        try:
            client = OpenAI(api_key=api_key)
            # 模型名以官网模型列表为准，这里选当前便宜够用的做示例，可能已有更新
            resp = client.responses.create(model="gpt-5-mini", input=prompt)
            print("[4] 模型回答：")
            print(resp.output_text)
        except Exception as exc:
            print(f"[4] 生成阶段出错（网络/额度等原因）：{exc}")
