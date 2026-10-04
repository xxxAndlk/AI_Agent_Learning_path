# -*- coding: utf-8 -*-
"""第05课演示：检索器（Retriever）怎么找资料、怎么接进链。

三段结构：
  1) 纯标准库迷你检索——cosine 相似度 + top-k，零依赖，离线可真跑；
  2) LangChain InMemoryVectorStore + 手工embedding——装了 langchain-core 即可离线跑；
  3) 换真实嵌入模型/接完整链的写法——需 API Key，本机未实跑，仅作示范（见文件末注释）。

pip install langchain langchain-core python-dotenv
"""

import math
import sys

# ---------- 第一段：纯标准库的迷你检索（离线可真跑） ----------

# 手工小向量：把每块资料压成 3 个数，肉眼能看懂。真实嵌入是几百上千维，
# 但"比较两个向量方向是否接近"的数学一模一样。三个维度假装对应三种话题。
DOCS = [
    {"text": "报销流程：在系统提交发票照片，主管审批后财务打款。",
     "meta": {"source": "员工手册.md", "page": 2},
     "vec": [0.9, 0.1, 0.0]},
    {"text": "向量检索：把文字变成向量，按距离找最相关的几块。",
     "meta": {"source": "langchain笔记.md", "page": 5},
     "vec": [0.0, 1.0, 0.1]},
    {"text": "对话记忆：模型默认无状态，可用窗口或摘要保留前文。",
     "meta": {"source": "langchain笔记.md", "page": 3},
     "vec": [0.0, 0.2, 1.0]},
    {"text": "差旅报销标准：高铁二等座实报实销，住宿每晚限额 400 元。",
     "meta": {"source": "财务制度.md", "page": 7},
     "vec": [0.8, 0.0, 0.1]},
]


def cosine(a, b):
    """余弦相似度：两个向量夹角越小，值越接近 1，意思越接近。"""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0  # 零向量没有方向，直接算不相关
    return dot / (norm_a * norm_b)


def mini_retrieve(query_vec, k=2):
    """迷你检索器三步：算相似度 → 排序 → 取前 k 个。讲义第三节的原理就是它。"""
    scored = [(cosine(query_vec, d["vec"]), d) for d in DOCS]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return scored[:k]


def part1():
    print("== 第 1 段：纯标准库迷你检索（零依赖，离线真跑） ==")
    query_vec = [0.85, 0.05, 0.0]  # "报销限额是多少？"的手工版嵌入
    for score, doc in mini_retrieve(query_vec, k=2):
        print(f"score={score:.3f}  {doc['meta']}  {doc['text']}")


# ---------- 第二段：同样的活儿交给 LangChain ----------

def _toy_vec(text):
    """手工embedding：命中哪个话题的关键词就点亮哪个维度。
    易错点：入库和查询必须用同一套向量化规则，否则坐标对不上。"""
    v = [0.0, 0.0, 0.0]
    if "报销" in text or "发票" in text:
        v[0] = 1.0
    if "向量" in text or "检索" in text:
        v[1] = 1.0
    if "记忆" in text or "窗口" in text:
        v[2] = 1.0
    return v


def part2():
    print("\n== 第 2 段：LangChain InMemoryVectorStore（装了 langchain 即可离线跑） ==")
    try:
        from langchain_core.documents import Document
        from langchain_core.embeddings import Embeddings
        from langchain_core.vectorstores import InMemoryVectorStore
    except ImportError:
        print("未安装 langchain-core，本段跳过演示（pip install langchain）")
        return

    class ToyEmbeddings(Embeddings):
        """手工embedding：实现 embed_documents / embed_query 两个方法，
        就能顶替真实嵌入模型塞给向量库——接口对上，一切照常。"""

        def embed_documents(self, texts):
            return [_toy_vec(t) for t in texts]

        def embed_query(self, text):
            return _toy_vec(text)

    docs = [Document(page_content=d["text"], metadata=d["meta"]) for d in DOCS]
    store = InMemoryVectorStore(ToyEmbeddings())
    store.add_documents(docs)
    retriever = store.as_retriever(search_kwargs={"k": 2})  # 一行拿到检索器

    for doc in retriever.invoke("发票怎么报销？"):
        print(doc.metadata, doc.page_content)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # 防 Windows 控制台 GBK 乱码
    part1()
    part2()

# ---------- 第三段：换真实模型、接进链（需 API Key，本机未实跑） ----------
# ToyEmbeddings 换成真实嵌入服务即可，检索器用法一行不改——统一接口的意义就在这。
# Key 一律从环境变量读（可配合 python-dotenv 从 .env 读，.env 不要提交），严禁写死：
#
#   import os
#   from langchain_openai import OpenAIEmbeddings
#
#   embeddings = OpenAIEmbeddings(
#       model="text-embedding-3-small",  # 示例名，可能已更新：按官网模型列表选
#       api_key=os.environ.get("OPENAI_API_KEY"),  # 没设置则为 None，调用时才会报错
#   )
#   store = InMemoryVectorStore(embeddings)
#   retriever = store.as_retriever(search_kwargs={"k": 4})
#
# 接完整 RAG 链（检索→拼资料→填提示→问模型）见讲义第四节的 rag_chain，同样需 Key。
