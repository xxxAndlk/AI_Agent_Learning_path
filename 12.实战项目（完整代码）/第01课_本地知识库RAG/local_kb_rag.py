# -*- coding: utf-8 -*-
"""本地知识库 RAG（第01课实战项目）：文档入库 -> 检索相关段落 -> 带出处回答。

零依赖可跑（纯标准库）：
    python local_kb_rag.py                 # 内置演示：入库/检索/回答
    python local_kb_rag.py ask "年假有几天"  # 单独提问

可选升级（需 API Key，未实跑）：pip install openai，并设置环境变量 OPENAI_API_KEY，
程序会自动用真实模型把资料组织成回答；未配置时退回抽取式兜底。
"""

import json
import os
import re
import sys
import tempfile

# Windows 控制台默认 GBK，避免打印中文/符号时乱码
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KB_PATH = os.path.join(tempfile.gettempdir(), "mini_kb.json")

# ---------------------------------------------------------------- 示例文档
# 真实使用时，把这段换成读你自己的 txt/md 文件即可
DOCS = {
    "员工手册": (
        "入职与试用期：新员工入职即签订劳动合同，试用期为三个月，"
        "试用期通过后享受正式员工全部福利。\n\n"
        "年假：入职满一年每年 5 天，满三年每年 10 天，满五年每年 15 天。"
        "年假当年有效，原则上不跨年累积，需提前三个工作日在系统申请。\n\n"
        "考勤：工作日 9:00-18:00，午休一小时。每月可有两次弹性打卡，"
        "超过需部门负责人审批。"
    ),
    "报销制度": (
        "差旅报销：机票和高铁票实报实销，住宿每晚上限 400 元，"
        "需在返程后 10 个工作日内提交发票。\n\n"
        "餐饮报销：加班超过 20:00 可报销晚餐，上限 40 元；"
        "客户招待餐费需事先审批，人均上限 150 元。"
    ),
    "IT账号指南": (
        "VPN 申请：在 IT 服务台提交工单，注明姓名、部门与用途，"
        "审批通过后收到含安装包与配置文件的邮件，按指引安装即可。\n\n"
        "密码重置：登录门户点击忘记密码，通过绑定手机验证后自助重置；"
        "连续输错五次账号将锁定 30 分钟。\n\n"
        "软件安装：办公电脑统一由 IT 推送基础软件，"
        "特殊开发工具需部门负责人邮件批准后由 IT 协助安装。"
    ),
}


# ---------------------------------------------------------------- 入库
def build_kb(docs):
    """把每份文档按空行切段，登记出处（哪份文档第几段）。"""
    chunks = []
    for doc_name, content in docs.items():
        for i, para in enumerate(content.split("\n\n"), 1):
            text = para.replace("\n", "").strip()
            if text:
                chunks.append({"text": text, "doc": doc_name, "idx": i})
    return {"chunks": chunks}


def save_kb(kb):
    with open(KB_PATH, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False)
    return KB_PATH


def load_kb():
    if os.path.exists(KB_PATH):
        with open(KB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


# ---------------------------------------------------------------- 检索
def bigrams(s):
    """中文没空格可分词，取相邻两字组合当"词"。标点不参与打分。"""
    s = re.sub(r"[，。？！、：；()\s]", "", s)
    return [s[i:i + 2] for i in range(len(s) - 1)] or ([s] if s else [])


def search(kb, question, top=2):
    """字词重合度打分：问题的每个二字组合在片段中出现一次得一分，归一化。"""
    grams = bigrams(question)
    scored = []
    for ch in kb["chunks"]:
        score = sum(1 for g in grams if g in ch["text"])
        if score:
            scored.append((score / max(len(grams), 1), ch))
    scored.sort(key=lambda x: -x[0])
    return scored[:top]


# ---------------------------------------------------------------- 回答
def ask_real_llm(question, hits):
    """可选：用真实模型把资料揉成一句通顺回答。缺 Key/缺库/失败都退回 None。"""
    if not os.environ.get("OPENAI_API_KEY"):
        return None
    try:
        from openai import OpenAI  # pip install openai
    except ImportError:
        print("（提示：未安装 openai 库，pip install openai 后可用真实模型回答）")
        return None
    context = "\n".join(f"[{c['doc']} 第{c['idx']}段] {c['text']}" for _, c in hits)
    try:
        client = OpenAI()
        resp = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),  # 示例名，按官网当前列表替换
            input=(
                "仅根据以下资料回答问题，一句话作答并在末尾注明出处。\n"
                f"资料：\n{context}\n\n问题：{question}"
            ),
        )
        return resp.output_text
    except Exception as e:
        print(f"（提示：调用模型失败：{e}，本次改用抽取式回答）")
        return None


def ask(kb, question):
    hits = search(kb, question)
    if not hits:
        return "知识库里没找到相关内容，换个说法试试。", []
    ans = ask_real_llm(question, hits)
    if ans is None:  # 兜底：直接端出最相关段落原文
        _, c = hits[0]
        ans = f"根据《{c['doc']}》第 {c['idx']} 段：{c['text']}"
    return ans, hits


# ---------------------------------------------------------------- 命令行
def demo():
    print("=" * 50)
    print("本地知识库 RAG · 内置演示（纯标准库，离线可跑）")
    print("=" * 50)
    kb = build_kb(DOCS)
    path = save_kb(kb)
    print(f"[入库] {len(DOCS)} 份文档切成 {len(kb['chunks'])} 段，已存到 {path}\n")

    questions = ["年假有几天", "加班餐费能报销吗", "VPN 怎么申请"]
    for q in questions:
        print(f"问：{q}")
        ans, hits = ask(kb, q)
        for s, c in hits:
            print(f"  命中 《{c['doc']}》第 {c['idx']} 段  相关度 {s:.0%}")
        print(f"答：{ans}\n")


def main():
    argv = sys.argv[1:]
    if argv and argv[0] == "ask" and len(argv) > 1:
        kb = load_kb()
        if kb is None:  # 首次直接提问则现建知识库
            kb = build_kb(DOCS)
            save_kb(kb)
        ans, hits = ask(kb, " ".join(argv[1:]))
        for s, c in hits:
            print(f"  命中 《{c['doc']}》第 {c['idx']} 段  相关度 {s:.0%}")
        print(f"答：{ans}")
        return
    demo()


if __name__ == "__main__":
    main()
