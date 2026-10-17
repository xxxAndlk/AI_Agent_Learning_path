# 本地知识库 RAG（第 01 课实战项目）

## 这是干什么的

把几份文档喂进一个小知识库，之后直接用中文提问：程序会检索出最相关的段落，给出带出处的回答（出自哪份文档、第几段），你可以随时翻回原文核实。

## 怎么装

- 零依赖：装好 Python 3.9+ 即可，不需要 pip install 任何东西。
- 可选升级：想让模型把资料揉成更通顺的回答——
- `pip install openai python-dotenv`
- 设置环境变量 `DEEPSEEK_API_KEY`（生成段连 DeepSeek，模型默认 deepseek-flash，可用 `DEEPSEEK_MODEL` 覆盖；没配也能跑，程序自动用抽取式回答兜底）
- 检索用本地 bigrams 字词重合度：DeepSeek 无 embedding 接口，生产可换 BGE/通义/智谱等嵌入模型

## 怎么跑

```
python local_kb_rag.py                  # 内置演示：入库 -> 检索 -> 回答
python local_kb_rag.py ask "年假有几天"   # 单独提问
```

## 文件说明

| 文件 | 说明 |
|------|------|
| 第01课.md | 讲义：项目思路、架构图、代码导读 |
| local_kb_rag.py | 核心程序，约 180 行，纯标准库 |

## 接下来可以改

- 把 `DOCS` 换成读你自己的 txt/md 文件（`open(path, encoding="utf-8")`）
- 把检索换成第 5 章的 Embedding 相似度，或接入第 7 章的 FAISS
- 学完第 14 章回来，给这个项目加一个 Streamlit 网页问答界面
