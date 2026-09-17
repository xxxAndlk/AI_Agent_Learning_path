# RAG 实战指南：给本仓库文档做一个智能问答机器人

> 本文是一份**动手教程**：从零开始，把当前仓库里 14 章 77 节的学习资料做成知识库，最终得到一个可以多轮追问、回答带出处引用的问答机器人。
>
> 配套章节：`4.2 LCEL表达式详解`、`5.1 Chunk策略`、`5.2 Embedding模型`、`5.3 RAG_Pipeline`、`8.1 Chroma向量数据库`、`12.1 本地知识库RAG`。
> 本文是"最短可跑通路径"，原理细节遇到不懂的地方回查对应章节。

---

## 目录

- [0 开工之前](#0-开工之前)
- [1 准备环境](#1-准备环境)
- [2 第一步：加载知识库文档](#2-第一步加载知识库文档)
- [3 第二步：切分文本块（Chunk）](#3-第二步切分文本块chunk)
- [4 第三步：向量化并建立索引（Chroma）](#4-第三步向量化并建立索引chroma)
- [5 第四步：只验证检索（先别接 LLM）](#5-第四步只验证检索先别接-llm)
- [6 第五步：接上 LLM，生成带引用的回答](#6-第五步接上-llm生成带引用的回答)
- [7 第六步：多轮对话（追问改写）](#7-第六步多轮对话追问改写)
- [8 第七步：Streamlit Web UI](#8-第七步streamlit-web-ui)
- [9 第八步：评测与调优](#9-第八步评测与调优)
- [10 收尾：代码清单与学习地图](#10-收尾代码清单与学习地图)
- [附录 A 常见报错速查](#附录-a-常见报错速查)
- [附录 B 零成本本地方案（Ollama）](#附录-b-零成本本地方案ollama)
- [附录 C 参数速查表](#附录-c-参数速查表)

---

## 0 开工之前

### 0.1 最终效果

做完之后你会得到这样一个东西：

```text
你 > 5.1 里讲了哪几种切分策略，各自的坑是什么？

机器人 > 5.1 一共讲了 4 类切分策略 ...（正文）
        [来源: 05.RAG系统（重点）/5.1_Chunk策略.md › 5.1 Chunk策略 › 4 核心概念]
        [来源: 05.RAG系统（重点）/5.1_Chunk策略.md › 5.1 Chunk策略 › 7 常见问题]

你 > 那递归切分呢，重叠多少合适？      ← 追问，不用重复主语

机器人 > ...（结合上一轮的语境继续回答）
```

### 0.2 知识库范围

| 纳入 | 排除 |
|------|------|
| 01~14 章目录下全部 `.md`（77 节） | `README.md`（项目介绍，不是知识内容） |
| `大纲.md` | `修改记录_v4.1~v4.4.md`（版本流水账） |
| 本文 `RAG实战指南_文档问答机器人.md` | `rag_qa_bot/`（本项目自己的代码） |

总量：**79 个文件、约 290 万字符**（实测）。**规模很小**，一次全量 embedding 的成本约几美分，检索延迟毫秒级——先用最简单的方案跑通，别一上来就上 Milvus。

> 不想让这份教程本身进知识库？把文件名加进 `config.py` 的 `EXCLUDE_FILES` 即可，下面的数字会相应变成 78 个文件。

### 0.3 整体架构

```text
┌──────────── 离线：建索引（只跑一次，改了文档再跑） ────────────┐
│  .md 文件 → 加载 → 按标题切分 → Embedding → Chroma 持久化      │
└───────────────────────────────────────────────────────────────┘
┌──────────── 在线：问答（每次提问都走这条链） ──────────────────┐
│  提问 → 追问改写 → 向量检索 Top-K → 拼 Prompt → LLM → 带引用回答 │
└───────────────────────────────────────────────────────────────┘
```

### 0.4 目录规划

代码统一放在仓库根目录下新建的 `rag_qa_bot/`（这个目录会被加载器排除，机器人不会把自己的代码当知识库）：

```text
AI应用开发技术栈目录/
├── rag_qa_bot/
│   ├── .env              # API Key 等配置（不提交到 git）
│   ├── config.py         # 路径 / 模型名 / 参数
│   ├── check_env.py      # 连通性自检
│   ├── ingest.py         # 加载 + 切分（步骤 2、3）
│   ├── build_index.py    # 建库（步骤 4）
│   ├── retrieve.py       # 检索调试 CLI（步骤 5）
│   ├── rag.py            # RAG 链 + 多轮对话 + CLI（步骤 6、7）
│   ├── app.py            # Streamlit UI（步骤 8）
│   ├── evaluate.py       # 评测（步骤 9）
│   └── chroma_db/        # 向量库落盘目录（不提交到 git）
├── 01.Python快速入门（Go开发者版）/
└── ...
```

顺手把这两行加进仓库根目录的 `.gitignore`（**别把 API Key 提交上去**）：

```gitignore
rag_qa_bot/.env
rag_qa_bot/chroma_db/
```

### 0.5 时间预算

| 阶段 | 耗时 |
|------|------|
| 环境 + 自检 | 15 分钟 |
| 跑通全流程（步骤 2~6） | 40 分钟 |
| Web UI + 评测 | 30 分钟 |
| 建索引实际等待时间 | 全量 3~8 分钟（取决于网络） |

---

## 1 准备环境

### 1.1 建虚拟环境

仓库文档里 Dockerfile 用的是 `python:3.11-slim`。`chromadb`、`sentence-transformers` 这类带二进制的包，**用 3.11 / 3.12 最省心**；本机是 3.14 的话如果装 `chromadb` 报"找不到 wheel"，就退回 3.12 重建环境。

```bash
cd "D:\data\demo\py_AI_doc\AI应用开发技术栈目录"
mkdir rag_qa_bot && cd rag_qa_bot

py -3.12 -m venv .venv            # Windows 有多个 Python 版本时用 py -3.12
.venv\Scripts\activate            # Git Bash: source .venv/Scripts/activate
python -m pip install -U pip
```

### 1.2 安装依赖

```bash
# 核心依赖：LangChain v1.x + OpenAI 兼容 SDK + Chroma
pip install "langchain>=1.0" langchain-core langchain-openai langchain-community langchain-text-splitters langchain-chroma chromadb python-dotenv

# 第七步 UI 用
pip install streamlit

# 进阶可选（先不装，步骤 9 再回来）
# pip install rank_bm25 sentence-transformers
```

各包分工（对应 `4.1 LangChain基础与架构` 里的模块划分）：

| 包 | 用途 |
|----|------|
| `langchain-openai` | `ChatOpenAI`（LLM）、`OpenAIEmbeddings`（向量化） |
| `langchain-text-splitters` | `MarkdownHeaderTextSplitter`、`RecursiveCharacterTextSplitter` |
| `langchain-chroma` + `chromadb` | 向量库读写、本地持久化 |
| `langchain-community` | 进阶用的检索器（BM25、CrossEncoder 重排） |
| `python-dotenv` | 从 `.env` 读配置 |

### 1.3 配置 .env

新建 `rag_qa_bot/.env`：

```env
OPENAI_API_KEY=sk-你的key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-5.4-mini
EMBEDDING_MODEL=text-embedding-3-small
```

国内中转网关、或本地 Ollama，只改 `OPENAI_BASE_URL` 和模型名即可（见附录 B）。**注意**：`OPENAI_BASE_URL` 要带 `/v1`，不要带结尾斜杠。

### 1.4 config.py：所有配置集中一处

```python
# rag_qa_bot/config.py
import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

PROJECT_DIR = Path(__file__).resolve().parent
REPO_ROOT = PROJECT_DIR.parent           # 仓库根目录 = 知识库根目录
PERSIST_DIR = PROJECT_DIR / "chroma_db"  # Chroma 落盘目录
COLLECTION_NAME = "ai_stack_docs"

load_dotenv(PROJECT_DIR / ".env")

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.4-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "120"))
TOP_K = int(os.getenv("TOP_K", "6"))

# 加载知识库时排除的文件 / 目录
EXCLUDE_FILES = {"README.md"}
EXCLUDE_PREFIXES = ("修改记录_",)
EXCLUDE_DIRS = {PROJECT_DIR.name, ".git", ".venv", "venv", "__pycache__"}


def get_llm(temperature: float = 0.0) -> ChatOpenAI:
    """问答场景 temperature=0：稳定、少随机，降低幻觉。"""
    return ChatOpenAI(model=LLM_MODEL, temperature=temperature)


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)
```

### 1.5 check_env.py：30 秒连通性自检

**先验证钥匙能开门，再谈做事。** 很多"RAG 没效果"最后查出来是 Key 或 Base URL 配错了。

```python
# rag_qa_bot/check_env.py
from config import EMBEDDING_MODEL, LLM_MODEL, get_embeddings, get_llm

llm = get_llm()
reply = llm.invoke("只回复两个字：收到")
print(f"[OK] LLM {LLM_MODEL} 可用：{reply.content}")

vec = get_embeddings().embed_query("测试一句话")
print(f"[OK] Embedding {EMBEDDING_MODEL} 可用，向量维度：{len(vec)}")
```

```bash
python check_env.py
# [OK] LLM gpt-5.4-mini 可用：收到
# [OK] Embedding text-embedding-3-small 可用，向量维度：1536
```

**检查点**：两行都打 `[OK]` 才继续。报错对照附录 A。

---

## 2 第一步：加载知识库文档

### 2.1 做什么

把仓库里的 `.md` 文件读成 LangChain 的 `Document` 对象，每个对象带好**元数据**（相对路径、所属章节目录）。元数据现在不起眼，到"回答带引用"和"按章节过滤检索"时会变成刚需。

对应 `5.3 RAG Pipeline` 的"文档加载"环节。

### 2.2 为什么不用 DirectoryLoader

`DirectoryLoader` + glob 也能加载，但排除规则（排除 README、排除 `修改记录_*`、排除自己这个目录）写起来很别扭。这里手工 `rglob` 一遍，规则一目了然，也方便你随时改。

### 2.3 ingest.py：加载部分

```python
# rag_qa_bot/ingest.py
import sys
from pathlib import Path

from langchain_core.documents import Document

import config


def iter_markdown_files() -> list[Path]:
    """遍历仓库里的知识库文件，排除 README、修改记录、项目自身目录。"""
    files: list[Path] = []
    for path in sorted(config.REPO_ROOT.rglob("*.md")):
        if any(part in config.EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in config.EXCLUDE_FILES:
            continue
        if path.name.startswith(config.EXCLUDE_PREFIXES):
            continue
        files.append(path)
    return files


def load_documents() -> list[Document]:
    docs: list[Document] = []
    for path in iter_markdown_files():
        rel = path.relative_to(config.REPO_ROOT).as_posix()   # 统一用 /，Windows 上也一致
        text = path.read_text(encoding="utf-8")
        chapter = rel.split("/")[0] if "/" in rel else "根目录"
        docs.append(
            Document(
                page_content=text,
                metadata={"source": rel, "chapter": chapter, "chars": len(text)},
            )
        )
    return docs


if __name__ == "__main__" and len(sys.argv) == 1:
    docs = load_documents()
    total_chars = sum(d.metadata["chars"] for d in docs)
    print(f"加载文件数：{len(docs)}")
    print(f"总字符数：{total_chars:,}")
    for d in docs[:3]:
        print(f"  - {d.metadata['source']}（{d.metadata['chars']:,} 字符）")
```

```bash
python ingest.py
# 加载文件数：79
# 总字符数：2,936,478
#   - 01.Python快速入门（Go开发者版）/1.1_Python_vs_Go_关键差异速查.md（...）
```

### 2.4 检查点

- 文件数 **79**（77 节 + `大纲.md` + 本指南）。明显偏少 → 排除规则写错（比如把章节目录名也排除了）。
- 抽查几条，`source` 里没有 `README.md`、没有 `修改记录_`、没有 `rag_qa_bot/`。

### 2.5 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| Windows 报 `UnicodeDecodeError` | 文档含非 UTF-8 字符 | 本仓库已统一 UTF-8（v4.4 校订说明）；外部文档加 `errors="ignore"` 兜底 |
| `source` 里出现 `\` 反斜杠 | 直接 `str(path)` 的结果 | 用 `as_posix()`，跨平台一致 |
| 大文件如 `12.1`（145 KB）拖慢加载 | 加载本身很快，慢的是后面的切分和 embedding | 正常现象，步骤 4 会看到进度条 |

---

## 3 第二步：切分文本块（Chunk）

### 3.1 做什么

把每个大文档切成 **500~1000 字符**的小块。这是整个 RAG 里**最值得花时间调**的一步——切得好，检索基本就对了。

对应 `5.1 Chunk策略`，本教程用它的推荐组合：**结构感知切分 + 递归字符切分**。

### 3.2 为什么这么切

这份知识库是**高度结构化的 Markdown**：标题分级、正文、代码块、表格。所以两步走：

1. **`MarkdownHeaderTextSplitter`**：先按 `# / ## / ###` 切成"小节"，并把标题内容写进元数据（`h1/h2/h3`）。这样每个块都自带"我在哪一节"，回答引用和上下文都靠它。
2. **`RecursiveCharacterTextSplitter`**：小节超过 `chunk_size` 的再按优先级切：段落 → 标题 → 换行 → 中文句号 → 分号 → 逗号。**中文文档一定要把 `。；，` 加进分隔符**，否则会从句子中间劈开。

### 3.3 ingest.py：切分部分

在 `ingest.py` 末尾追加：

```python
# rag_qa_bot/ingest.py（续，追加到文件末尾）
import re

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)

HEADERS_TO_SPLIT_ON = [("#", "h1"), ("##", "h2"), ("###", "h3")]

# 可选：把围栏代码块整体去掉。问"这段代码怎么写"别开；问"讲了什么概念"可开，
# 能明显减少代码噪声对语义检索的干扰（本仓库有 1100+ 个代码块）。
CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)


def split_documents(
    docs: list[Document],
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP,
    strip_code_blocks: bool = False,
) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS_TO_SPLIT_ON,
        strip_headers=False,          # 标题留在正文里，检索时更"有信息量"
    )
    char_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        keep_separator=True,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", "；", "，", " ", ""],
    )

    chunks: list[Document] = []
    for doc in docs:
        text = CODE_BLOCK_RE.sub("\n[代码块已省略]\n", doc.page_content) if strip_code_blocks else doc.page_content
        for piece in header_splitter.split_text(text):
            merged_meta = {**doc.metadata, **piece.metadata}
            for chunk in char_splitter.split_documents([Document(page_content=piece.page_content, metadata=merged_meta)]):
                chunks.append(chunk)
    return chunks


if __name__ == "__main__" and len(sys.argv) > 1:
    all_chunks = split_documents(load_documents())
    sizes = [len(c.page_content) for c in all_chunks]
    print(f"切分后块数：{len(all_chunks)}")
    print(f"块长度：min={min(sizes)} 平均={sum(sizes) // len(sizes)} max={max(sizes)}")
```

运行看看：

```bash
python ingest.py split
# 切分后块数：5000 左右（你的数字会有浮动）
# 块长度：min=45 平均=520 max=812
```

### 3.4 检查点

- **块数**在 3000~8000 之间算正常（约 290 万字符 / 平均 500 字符）。
- **平均长度**明显小于 `chunk_size`（800）是好事：说明大多数小节本来就够短，切得自然。
- 抽查任意 3 个块，看内容是不是完整句子和小节，而不是半截代码。

```python
# 抽查用（可临时加到 if __name__ 块里）
for c in all_chunks[:3]:
    print("=" * 60)
    print(c.metadata)
    print(c.page_content[:300])
```

### 3.5 参数怎么调

| 参数 | 调大 | 调小 |
|------|------|------|
| `chunk_size` | 上下文更完整，但检索精度下降、更贵 | 检索更准，但容易答不全 |
| `chunk_overlap` | 边界信息不容易丢，代价是块数变多 | 调到 0 会切断跨块的连续论述 |

经验值：**中文技术文档，800 / 120 先跑起来**，步骤 9 的评测会告诉你到底要不要改。

### 3.6 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 块里出现半个代码块 / 括号不闭合 | 递归切分在 ```` ``` ```` 处不感知语言边界 | 要么开 `strip_code_blocks`，要么把 `chunk_size` 调大到 1200+ |
| 块里只有标题没有正文 | 文档里存在空小节 | 在切分后过滤：`len(chunk.page_content) < 50` 的直接丢弃 |
| 检索总是命中表格 | 表格被切成独立的块，短且关键词密集 | 正常现象；可用步骤 5 的 `filter` 按章节缩小范围 |

---

## 4 第三步：向量化并建立索引（Chroma）

### 4.1 做什么

把每个块用 Embedding 模型转成 1536 维向量，连同原文、元数据一起存进 Chroma，落盘到 `rag_qa_bot/chroma_db/`。**只跑一次**，改了文档再重跑。

对应 `5.2 Embedding模型` + `8.1 Chroma向量数据库`。

### 4.2 三个关键决策

1. **向量库选 Chroma**：Python 原生、免服务、自带落盘，是 `8.3 向量数据库选型指南` 里"快速原型"的首选。数据量到百万级再考虑 Milvus。
2. **相似度用 cosine**：OpenAI 系 embedding 训练时就是按余弦相似度用的，所以建 collection 时显式指定 `hnsw:space = cosine`，别用默认的 L2。**这个不指定，检索质量会莫名变差。**
3. **ID 用"文件路径 + 序号"**：确定性 ID 带来幂等——同一个块重复写入是覆盖而不是新增。想增量更新时只 add 变化的文件即可。

### 4.3 build_index.py

```python
# rag_qa_bot/build_index.py
import shutil
import sys
import time

from langchain_chroma import Chroma

import config
from ingest import load_documents, split_documents


def get_vectorstore() -> Chroma:
    return Chroma(
        collection_name=config.COLLECTION_NAME,
        embedding_function=config.get_embeddings(),
        persist_directory=str(config.PERSIST_DIR),
        collection_metadata={"hnsw:space": "cosine"},   # 关键：用余弦距离
    )


def build(rebuild: bool = False) -> None:
    if config.PERSIST_DIR.exists():
        if not rebuild:
            print(f"索引已存在：{config.PERSIST_DIR}（要重建请加 --rebuild）")
            return
        shutil.rmtree(config.PERSIST_DIR)
        print("已删除旧索引，开始重建")

    chunks = split_documents(load_documents())
    ids = [f"{c.metadata['source']}#{i}" for i, c in enumerate(chunks)]

    vs = get_vectorstore()
    batch = 64
    started = time.time()
    for i in range(0, len(chunks), batch):
        vs.add_documents(chunks[i : i + batch], ids=ids[i : i + batch])
        done = min(i + batch, len(chunks))
        print(f"  写入 {done}/{len(chunks)} 块，用时 {time.time() - started:.0f}s")

    print(f"完成。集合 {config.COLLECTION_NAME} 共 {vs._collection.count()} 条向量")


if __name__ == "__main__":
    build(rebuild="--rebuild" in sys.argv)
```

```bash
python build_index.py
# 写入 64/5031 块，用时 3s
# ...
# 完成。集合 ai_stack_docs 共 5031 条向量
```

全量约 5000 块，`text-embedding-3-small` 的成本大约 **几美分**，别怕重跑。

### 4.4 检查点

```bash
python build_index.py            # 第二次运行应直接提示"索引已存在"
ls chroma_db                     # 应该能看到 chroma.sqlite3
```

### 4.5 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 换 Embedding 模型后检索全乱 | 维度/向量空间变了，旧索引没意义 | `python build_index.py --rebuild`，**换模型必须重建** |
| 写入报 429 / 超时 | 并发太高或网络抖动 | 把 `batch` 调到 16 重试；已写入的块不会重复计费 |
| `chroma_db` 里没有 sqlite 文件 | 用了 `Chroma.from_documents` 但没给 `persist_directory` | 本教程的 `get_vectorstore()` 已固定传参，照抄即可 |
| 想换向量库（FAISS/PGVector） | 接口不同 | `7.x` / `8.5` 有对照写法；上层代码只依赖 `similarity_search*` 和 `as_retriever`，换库改动很小 |

---

## 5 第四步：只验证检索（先别接 LLM）

### 5.1 为什么先做这一步

**RAG 的问题 90% 出在检索，不生成。** 检索错了，模型再强也只能在错误上下文里编。所以先单测检索：不接 LLM，直接看"我这个问题，召回的都是什么块、相似度多少、来自哪个文件"。

这一步的产出是一个**自测问题清单**，步骤 9 的评测直接复用。

### 5.2 retrieve.py：检索调试 CLI

```python
# rag_qa_bot/retrieve.py
import sys

from langchain_core.documents import Document

import config
from build_index import get_vectorstore


def show(docs: list[Document], scores: list[float] | None = None) -> None:
    for rank, doc in enumerate(docs, 1):
        m = doc.metadata
        title = " › ".join(x for x in [m.get("h1"), m.get("h2"), m.get("h3")] if x)
        score = f"{scores[rank - 1]:.3f}" if scores else "  -  "
        print(f"\n[{rank}] 相似度 {score} | {m['source']}")
        if title:
            print(f"    小节：{title}")
        print("    " + doc.page_content[:160].replace("\n", " ") + " ...")


def search(query: str, k: int = config.TOP_K, chapter: str | None = None, mmr: bool = False) -> None:
    vs = get_vectorstore()
    flt = {"chapter": chapter} if chapter else None

    if mmr:
        docs = vs.max_marginal_relevance_search(query, k=k, fetch_k=20, filter=flt)
        print(f"MMR 检索：{query}（k={k}，fetch_k=20）")
        show(docs)
        return

    # Chroma cosine 空间返回的是"距离"，越小越像。1 - 距离 = 相似度。
    pairs = vs.similarity_search_with_score(query, k=k, filter=flt)
    print(f"向量检索：{query}（k={k}，filter={flt}）")
    show([d for d, _ in pairs], [1.0 - s for _, s in pairs])


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('用法：python retrieve.py "你的问题" [--chapter 05.RAG系统（重点）] [--mmr]')
        sys.exit(1)

    args = sys.argv[1:]
    question = args[0]
    chapter = args[args.index("--chapter") + 1] if "--chapter" in args else None
    search(question, chapter=chapter, mmr="--mmr" in args)
```

### 5.3 跑一组"标准问题"

先用**已知答案**的问题验证召回，答对的标准是"召回的块里确实包含答案所在的小节"：

```bash
python retrieve.py "RAG 和微调的区别是什么"
python retrieve.py "5.1 里讲了哪几种切分策略"
python retrieve.py "LCEL 的管道操作符怎么用"
python retrieve.py "Chroma 怎么做元数据过滤"
python retrieve.py "BGE-M3 的向量维度是多少"
python retrieve.py "12.1 那个项目用什么做 UI"
```

同时验证元数据过滤和 MMR：

```bash
python retrieve.py "重排序怎么做" --chapter "05.RAG系统（重点）"
python retrieve.py "Agent 的记忆系统怎么设计" --mmr
```

### 5.4 检查点

对照下表判断，哪一条不满足就修哪一条：

| 症状 | 判断 | 处理 |
|------|------|------|
| Top-1 就是答案所在小节 | 检索健康，进入第五步 | — |
| 答案在第 3~6 名 | 召回够用但不精 | 步骤 9 加 Rerank，或把 `k` 调到 8 |
| 相似度都低于 0.3 且不相关 | 召回失败 | 先查问题表述是否用了文档里的词 → 再开 `strip_code_blocks` 重建 → 换中文更强的 embedding（`bge-m3`） |
| 前 3 名全来自同一个文件、内容重复 | MMR 该上场了 | 加 `--mmr`，它会在"相关"和"多样"之间做平衡 |
| 问代码怎么写，召回全是概念解释 | 你的索引里代码被弱化了 | 重建时关掉 `strip_code_blocks` |

### 5.5 关于相似度阈值的正确用法

别用"相似度低于 0.75 就拒答"这种硬阈值——**cosine 相似度的绝对值在不同 embedding 模型间不可比**，同一句问题在 `text-embedding-3-small` 上可能是 0.45，换个模型就变成 0.72。更稳的做法是让 LLM 判断"上下文是否足够回答"（写进 Prompt，见 6.3）。

---

## 6 第五步：接上 LLM，生成带引用的回答

### 6.1 做什么

拿上一步召回的 Top-K 块拼成上下文，加上"只依据上下文回答 + 标注出处 + 不知道就说不知道"的 Prompt，走 LCEL 链输出答案和来源列表。

对应 `5.3 RAG Pipeline` 的生成环节 + `4.2 LCEL表达式详解`。

### 6.2 上下文怎么拼：把元数据变成引用

关键点：**块本身不带"我是谁"的信息，但元数据带**。拼接时把 `文件 › 小节` 写在每段前面，模型就能顺手引用它。

```text
[05.RAG系统（重点）/5.1_Chunk策略.md › 5.1 Chunk策略 › 4 核心概念]
（正文……）

---

[04.LangChain框架详解/4.2_LCEL表达式详解.md › 4.2 LCEL表达式详解 › 3 工作原理]
（正文……）
```

### 6.3 rag.py：RAG 链 + 单轮问答

```python
# rag_qa_bot/rag.py
import sys

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

import config
from build_index import get_vectorstore

SYSTEM_PROMPT = """你是「AI 应用开发技术栈」学习资料的答疑助手。

规则：
1. 只依据 <上下文> 回答。上下文里没有的信息，直接说「资料里没有提到」，不要凭常识补充，更不要编造。
2. 用中文回答，尽量具体：参数、结论、代码要点都从上下文里取，别泛泛而谈。
3. 每个关键结论后用 [来源: 文件路径 › 小节标题] 标注出处，最多标 3 处。
4. 如果多个文档结论有冲突，指出冲突并分别标注来源。
5. 回答末尾用一句话说明「依据的是哪几个小节」，方便读者回查。"""

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "<上下文>\n{context}\n</上下文>\n\n问题：{question}"),
    ]
)


def format_docs(docs: list[Document]) -> str:
    blocks = []
    for d in docs:
        m = d.metadata
        title = " › ".join(x for x in [m.get("h1"), m.get("h2"), m.get("h3")] if x)
        head = m["source"] if not title else f"{m['source']} › {title}"
        blocks.append(f"[{head}]\n{d.page_content}")
    return "\n\n---\n\n".join(blocks)


def build_answer_chain(k: int = config.TOP_K):
    retriever = get_vectorstore().as_retriever(search_kwargs={"k": k})

    def retrieve(inputs: dict) -> dict:
        docs = retriever.invoke(inputs["question"])
        return {"context": format_docs(docs), "question": inputs["question"], "docs": docs}

    return (
        RunnableLambda(retrieve)
        | RunnablePassthrough.assign(answer=ANSWER_PROMPT | config.get_llm() | StrOutputParser())
    )


def ask(question: str) -> dict:
    """单轮问答，返回 {answer, docs}。"""
    result = build_answer_chain().invoke({"question": question})
    return {"answer": result["answer"], "docs": result["docs"]}


def print_result(question: str, result: dict) -> None:
    print(f"\n问：{question}\n")
    print(result["answer"])
    print("\n召回的来源：")
    for i, d in enumerate(result["docs"], 1):
        m = d.metadata
        title = " › ".join(x for x in [m.get("h1"), m.get("h2"), m.get("h3")] if x)
        print(f"  [{i}] {m['source']}" + (f" › {title}" if title else ""))


if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "这个仓库一共有几章？各自讲什么？"
    print_result(q, ask(q))
```

```bash
python rag.py "RAG 和微调的区别是什么"
```

期望输出：一段 3~6 行的中文回答，每个结论后面跟着 `[来源: 05.RAG系统（重点）/5.3_RAG_Pipeline.md › ... › 2.3 RAG vs 微调]`，末尾有来源小结。

### 6.4 检查点

| 测什么 | 期望 |
|--------|------|
| 常规问题（`"5.1 讲了哪几种切分策略"`） | 答案完整，引用的小节和 `retrieve.py` 的召回结果对得上 |
| 知识库外的问题（`"今天天气怎么样"`） | 明确说"资料里没有提到"，**不硬编** |
| 边界问题（`"12.1 项目的 requirements.txt 里有什么"`） | 能答出 `langchain>=0.1.0`、`faiss-cpu`、`chromadb` 等 |

第三行如果是"资料里没有提到"，多半是分块把那个代码块切散了——回步骤 3 调 `chunk_size` 或关掉 `strip_code_blocks` 重建。

### 6.5 这里已经内置的三个抗幻觉设计

1. `temperature=0`：降低随机性。
2. Prompt 里明确定义"不知道"的出口（规则 1）——不给出路，模型就会编。
3. 强制标注来源：**引用是幻觉的照妖镜**，答得再流畅，来源对不上就是没用。

---

## 7 第六步：多轮对话（追问改写）

### 7.1 做什么

用户追问"那递归切分呢，重叠多少合适？"——这句话单独拿去检索，"那""它"指代不清，向量检索会跑偏。标准解法是**查询改写（Query Rewrite / Condense）**：先让 LLM 结合历史把追问改写成独立问题，再拿改写后的问题去检索。对应 `5.4 RAG高级主题` 的查询重写。

```text
原始追问：  "那它的重叠参数呢？"
改写后：    "5.1 Chunk策略 中递归字符切分的 chunk_overlap 参数应该设置多少？"
```

### 7.2 rag.py：追加 RagChat 类和 CLI

在 `rag.py` 末尾追加：

```python
# rag_qa_bot/rag.py（续，追加到文件末尾）
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import MessagesPlaceholder

CONDENSE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "根据对话历史，把用户的最新问题改写成一个不依赖上文、可独立检索的完整问题。"
            "只输出改写后的问题，不要解释。若最新问题本身已完整，原样返回，不要画蛇添足。",
        ),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ]
)

CHAT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("history"),
        ("human", "<上下文>\n{context}\n</上下文>\n\n问题：{question}"),
    ]
)

MAX_HISTORY_MESSAGES = 6   # 只带最近 3 轮进 Prompt，控制 token


class RagChat:
    """带对话历史的 RAG 机器人：改写追问 → 检索 → 生成。"""

    def __init__(self, k: int = config.TOP_K) -> None:
        self.retriever = get_vectorstore().as_retriever(search_kwargs={"k": k})
        self.llm = config.get_llm()
        self.condense_chain = CONDENSE_PROMPT | self.llm | StrOutputParser()
        self.chat_chain = CHAT_PROMPT | self.llm | StrOutputParser()
        self.history: list[BaseMessage] = []

    def rewrite(self, question: str) -> str:
        if not self.history:
            return question
        return self.condense_chain.invoke(
            {"history": self.history[-MAX_HISTORY_MESSAGES:], "question": question}
        ).strip()

    def ask(self, question: str) -> dict:
        standalone = self.rewrite(question)
        docs = self.retriever.invoke(standalone)
        answer = self.chat_chain.invoke(
            {
                "history": self.history[-MAX_HISTORY_MESSAGES:],
                "context": format_docs(docs),
                "question": question,
            }
        )
        self.history += [HumanMessage(question), AIMessage(answer)]
        return {"answer": answer, "docs": docs, "standalone_question": standalone}


def chat_cli() -> None:
    bot = RagChat()
    print("输入问题开始对话（exit / quit 退出）")
    while True:
        try:
            question = input("\n你 > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit"}:
            break
        result = bot.ask(question)
        if result["standalone_question"] != question:
            print(f"（追问改写为：{result['standalone_question']}）")
        print(f"\n机器人 > {result['answer']}")
        for i, d in enumerate(result["docs"], 1):
            m = d.metadata
            title = " › ".join(x for x in [m.get("h1"), m.get("h2"), m.get("h3")] if x)
            print(f"  [{i}] {m['source']}" + (f" › {title}" if title else ""))
```

把入口改成支持两种模式（替换 `rag.py` 原来的 `if __name__ == "__main__"` 块）：

```python
if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--chat":
        chat_cli()
    else:
        q = sys.argv[1] if len(sys.argv) > 1 else "这个仓库一共有几章？各自讲什么？"
        print_result(q, ask(q))
```

### 7.3 跑一个多轮测试

```bash
python rag.py --chat
```

```text
你 > 5.1 讲了哪几种切分策略？
机器人 > ...（4 类：固定 / 递归 / 语义 / 结构化）
（追问改写为：5.1 Chunk策略 中递归字符切分的 chunk_size 和 chunk_overlap 应该怎么设置？）
你 > 那它们的参数怎么调？
机器人 > ...
```

### 7.4 检查点

- 第二轮的 `（追问改写为：...）` 里，主语被补全了，代词被替换成了具体名词。
- 改写的检索结果**明显比不改写好**——这是判断改写有没有生效的唯一标准。如果改写后召回更差，说明改写 Prompt 太爱发挥了，把 `"原样返回，不要画蛇添足"` 那句保留住。

### 7.5 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 多轮之后越答越飘 | 历史太长，早期无关内容干扰 | 调小 `MAX_HISTORY_MESSAGES`；`4.3 Memory组件详解` 里有摘要式记忆的写法 |
| 第一轮正常，追问全崩 | 没做改写 | 本节的 `RagChat.rewrite` 就是干这个的 |
| 想要流式输出 | `invoke` 是阻塞式的 | LCEL 链改 `stream()`；`4.2` 有 `astream` 写法，步骤 8 的 UI 会用到 |

---

## 8 第七步：Streamlit Web UI

### 8.1 做什么

套一个 Web 界面，支持连续对话、流式输出、点开看引用原文。对应 `14.3 Streamlit_Gradio_UI`，`12.1 本地知识库RAG` 第 10 节也是这么干的。

### 8.2 app.py

```python
# rag_qa_bot/app.py
import streamlit as st

from rag import RagChat

st.set_page_config(page_title="AI 技术栈答疑机器人", page_icon="🤖")
st.title("AI 应用开发技术栈 · 文档答疑机器人")
st.caption("知识库：本仓库 01~14 章全部文档（自动排除 README 与修改记录）")


@st.cache_resource
def get_bot() -> RagChat:
    return RagChat()


bot = get_bot()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("docs"):
            with st.expander(f"引用来源（{len(msg['docs'])} 条）"):
                for i, d in enumerate(msg["docs"], 1):
                    m = d.metadata
                    title = " › ".join(x for x in [m.get("h1"), m.get("h2"), m.get("h3")] if x)
                    st.markdown(f"**[{i}] {m['source']}**" + (f" › {title}" if title else ""))
                    st.code(d.page_content[:500], language="markdown")

question = st.chat_input("问点什么，比如：5.1 讲了哪几种切分策略？")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("检索并生成中……"):
            result = bot.ask(question)
        st.markdown(result["answer"])
        with st.expander(f"引用来源（{len(result['docs'])} 条）"):
            for i, d in enumerate(result["docs"], 1):
                m = d.metadata
                title = " › ".join(x for x in [m.get("h1"), m.get("h2"), m.get("h3")] if x)
                st.markdown(f"**[{i}] {m['source']}**" + (f" › {title}" if title else ""))
                st.code(d.page_content[:500], language="markdown")

    st.session_state.messages.append(
        {"role": "assistant", "content": result["answer"], "docs": result["docs"]}
    )
```

```bash
streamlit run app.py
# 浏览器打开 http://localhost:8501
```

### 8.3 检查点

- 连续问 3 轮有上下文关联的问题，第三轮还能答对（`RagChat` 实例被 `cache_resource` 缓存的副作用：**多用户会共享一份对话历史**，本地自己用无所谓；要上线就改成 per-session 创建）。
- 点开"引用来源"，能看到原文块，复制出来能在仓库里搜到。

### 8.4 想再进一步

| 想做的事 | 看仓库哪一节 |
|----------|--------------|
| 换成 FastAPI + WebSocket 的接口服务 | `14.1 FastAPI开发`、`14.2 AI聊天应用` |
| 流式输出（打字机效果） | `4.2 LCEL表达式详解`（`astream`）+ `14.3` |
| 打包成 Docker | `12.1` 第 11 节 |
| 多用户隔离会话 | `13.5 AI_SaaS架构` |

---

## 9 第八步：评测与调优

### 9.1 为什么必须做

没有评测的 RAG 调优就是玄学：改完 Prompt 感觉"好像好了点"，实际可能是这一题恰好蒙对。**先定基线，再改一个变量，再看数字。**

### 9.2 三类失败要分开看

```text
问题 → [检索] → 上下文 → [生成] → 答案
        ↑ 失败1        ↑ 失败2/3
```

| 类型 | 症状 | 归因方法 | 对症下药 |
|------|------|----------|----------|
| 失败 1：召回没中 | 上下文里压根没有答案 | `retrieve.py` 直接看 Top-K | 换 embedding、调 chunk、加混合检索 |
| 失败 2：召回了但排序靠后 | 答案在第 8 名，`k=6` 捞不着 | 把 `k` 调大看答案排名 | 上 Rerank（`5.6`） |
| 失败 3：上下文有但答错 | 检索没问题，生成跑偏 | 人工看上下文 vs 答案 | 改 Prompt、换更强的 LLM |

### 9.3 evaluate.py：命中率评测

原理：给每个问题标好"答案应该在哪些文件里"，只看召回的块有没有覆盖这些文件。**这个指标不用人工打分，能自动化跑。**

```python
# rag_qa_bot/evaluate.py
"""检索命中率评测：问题 → 期望文件 → 看召回是否命中。
先跑这个脚本，再回前面调参数，每次只改一个变量。"""

from rag import build_answer_chain

CASES = [
    {"q": "RAG 和微调的区别是什么", "expect": ["05.RAG系统（重点）/5.3_RAG_Pipeline.md"]},
    {"q": "5.1 里讲了哪几种切分策略", "expect": ["05.RAG系统（重点）/5.1_Chunk策略.md"]},
    {"q": "LCEL 的管道操作符怎么组合", "expect": ["04.LangChain框架详解/4.2_LCEL表达式详解.md"]},
    {"q": "Chroma 怎么做元数据过滤", "expect": ["08.向量数据库进阶/8.1_Chroma向量数据库.md"]},
    {"q": "BGE-M3 的向量维度是多少", "expect": ["05.RAG系统（重点）/5.2_Embedding模型.md"]},
    {"q": "重排序模型怎么用", "expect": ["05.RAG系统（重点）/5.6_Rerank模型.md"]},
    {"q": "FAISS 有哪些索引类型", "expect": ["07.向量数据库/7.2_FAISS高级用法.md"]},
    {"q": "12.1 项目的 requirements.txt 里有什么", "expect": ["12.实战项目（完整代码）/12.1_本地知识库RAG.md"]},
    {"q": "怎么防止 Prompt 注入", "expect": ["06.Agent系统与智能体/6.3_LLM安全与对齐.md"]},
    {"q": "多 Agent 之间怎么协作", "expect": ["06.Agent系统与智能体/6.9_Multi-Agent系统.md"]},
]


def main(k: int = 6) -> None:
    chain = build_answer_chain(k=k)
    hit = 0
    for case in CASES:
        docs = chain.invoke({"question": case["q"]})["docs"]
        sources = {d.metadata["source"] for d in docs}
        ok = any(e in sources for e in case["expect"])
        hit += ok
        mark = "✅" if ok else "❌"
        print(f"{mark} k={k} {case['q']}")
        if not ok:
            print(f"     未命中 {case['expect']}，实际召回：{sorted(sources)}")
    print(f"\n命中率：{hit}/{len(CASES)} = {hit / len(CASES):.0%}")


if __name__ == "__main__":
    main()
```

```bash
python evaluate.py
# ✅ k=6 RAG 和微调的区别是什么
# ...
# 命中率：9/10 = 90%
```

**基线目标**：先跑到 **≥ 80%**。低于这个数别急着调生成环节，先按 9.4 修检索。

### 9.4 按顺序调这四刀

每次只改一个，跑 `evaluate.py` 对比：

| 顺序 | 动作 | 预期效果 | 成本 |
|------|------|----------|------|
| 1 | `k` 从 6 调到 10 | 失败 2 的题会回来 | 免费，但上下文变长变贵 |
| 2 | 重建索引：关掉 `strip_code_blocks` 或把 `chunk_size` 调到 1200 | 代码类问题变好 | 几分钱 |
| 3 | 加 Rerank：先向量召回 20 条，再用 `bge-reranker` 精排取 4 条（`5.6` 有完整代码） | 普遍 +5~15% | 延迟 +100ms 左右 |
| 4 | 混合检索：`EnsembleRetriever` = BM25（关键词）+ 向量（语义），权重 0.4/0.6（`5.4`） | 专有名词、缩写类问题变好 | 需要 `rank_bm25` |

### 9.5 生成质量的评测

检索命中率之外，答案本身好不好只能靠人评。20 题足够，每题打三个勾：

| 维度 | 合格标准 |
|------|----------|
| 忠实度 | 答案里的每句结论都能在上下文里找到依据 |
| 完整性 | 答案覆盖了上下文里的关键点，没有漏 |
| 引用准确 | 标注的文件/小节确实包含该结论 |

想自动化可以看 `11.5 LLM评测体系` 里的 RAGAS 方案：用另一个 LLM 当裁判，自动算 `faithfulness` / `answer_relevancy` / `context_precision`。先在人工评测上把问题摸清楚，再决定要不要上。

---

## 10 收尾：代码清单与学习地图

### 10.1 你一共写了 8 个文件

| 文件 | 行数级别 | 职责 |
|------|----------|------|
| `config.py` | ~35 | 路径、模型名、参数、LLM/Embedding 工厂 |
| `check_env.py` | ~15 | 连通性自检 |
| `ingest.py` | ~80 | 加载 + 两级切分 |
| `build_index.py` | ~40 | 建库、增量/重建 |
| `retrieve.py` | ~45 | 检索调试 |
| `rag.py` | ~130 | RAG 链 + 多轮对话 + CLI |
| `app.py` | ~55 | Streamlit UI |
| `evaluate.py` | ~45 | 命中率评测 |

加起来的有效代码不到 450 行——**RAG 的门槛不在代码量，在切分、检索、评测这些"调"的地方**。

### 10.2 完整的运行顺序

```bash
cd rag_qa_bot
python check_env.py                      # 1. 自检
python build_index.py                    # 2. 建索引（改文档后加 --rebuild）
python retrieve.py "你的问题"             # 3. 调检索
python rag.py "你的问题"                  # 4. 单轮问答
python rag.py --chat                     # 5. 多轮对话
python evaluate.py                       # 6. 评测
streamlit run app.py                     # 7. Web UI
```

### 10.3 下一步学什么（回仓库对应章节）

| 想深入 | 看这里 |
|--------|--------|
| 切分策略的原理和对比 | `5.1 Chunk策略` |
| 中文 embedding 怎么选 | `5.2 Embedding模型` |
| RAG 全流程的每个环节 | `5.3 RAG_Pipeline` |
| 查询重写、混合检索、语义缓存 | `5.4 RAG高级主题` |
| GraphRAG、多跳推理、自适应 RAG | `5.5 RAG高级架构` |
| 重排序原理与 Cross-Encoder | `5.6 Rerank模型` |
| 向量库进阶（索引算法、PGVector） | `8.4 向量索引算法`、`8.5 PGVector` |
| 完整生产级 RAG 项目（含 Docker） | `12.1 本地知识库RAG` |
| RAG 平台的分层架构 | `13.2 RAG系统架构` |
| 评测体系 | `11.5 LLM评测体系` |

---

## 附录 A 常见报错速查

| 报错 / 现象 | 原因 | 处理 |
|-------------|------|------|
| `openai.AuthenticationError: 401` | Key 错、过期、或与 Base URL 不匹配 | 检查 `.env` 里 Key 和 `OPENAI_BASE_URL` 是否成对（中转 Key 配官方 URL 必报 404/401） |
| `404 Not Found` / `model_not_found` | 模型名在当前网关不存在 | 换成网关支持的模型名；Ollama 要用 `ollama list` 里已有的名字 |
| `APIConnectionError` / 超时 | 网络或代理问题 | 检查 `HTTP_PROXY`/`HTTPS_PROXY` 环境变量；或换 Base URL |
| embed_query 返回维度不是 1536 且检索异常 | 换了 embedding 模型但没重建索引 | `python build_index.py --rebuild` |
| `chromadb` 安装失败 / 找不到 wheel | Python 版本太新 | 换 Python 3.11 / 3.12 重建 venv |
| `UnicodeDecodeError` | 文件非 UTF-8 | 读取时加 `errors="ignore"`，或先把文件转成 UTF-8 |
| Streamlit 改了代码没生效 | `cache_resource` 缓存了旧对象 | 浏览器右上角 `Rerun`，或进程重启 |
| 回答全是"资料里没有提到" | 检索空手而归 | 先跑 `retrieve.py` 定位是不是召回问题 |
| 回答流畅但引用对不上 | 幻觉 | 检查 Prompt 里的规则 1、3 是否被删改；`temperature` 是否被调高 |

## 附录 B 零成本本地方案（Ollama）

不想花 API 钱，就本地跑。装 Ollama 后：

```bash
ollama pull qwen3:8b      # 生成用（按你机器显存选，中文能力够用）
ollama pull bge-m3        # Embedding 用（1024 维，5.2 推荐的开放中文模型）
```

`.env` 改成：

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen3:8b
EMBEDDING_MODEL=bge-m3
```

然后 **`python build_index.py --rebuild`**（embedding 换模型必须重建），其余代码一行不用改——这就是走 OpenAI 兼容协议的好处。

取舍：

| | 云 API | 本地 Ollama |
|---|---|---|
| 成本 | 几分钱（索引）+ 每次问答微量 | 0 |
| 速度 | 快（受网络影响） | 取决于显卡，CPU 会明显慢 |
| 隐私 | 文档内容上传 | 全本地 |
| 质量 | `gpt-5.4-mini` 级 | 8B 级，复杂问答差距明显 |

想完全离线不装 Ollama，也可以把 embedding 换成 `HuggingFaceEmbeddings(model_name="BAAI/bge-m3")`（需要 `pip install sentence-transformers`，首次下载约 2 GB）。

## 附录 C 参数速查表

| 参数 | 位置 | 默认 | 调大 | 调小 |
|------|------|------|------|------|
| `CHUNK_SIZE` | `.env` | 800 | 上下文更完整，精度下降 | 检索更准，易答不全 |
| `CHUNK_OVERLAP` | `.env` | 120 | 边界信息不易丢，块数变多 | 省成本，跨块论述易断 |
| `TOP_K` | `.env` | 6 | 召回率↑、噪声↑、更贵 | 精度↑、易漏 |
| `strip_code_blocks` | `ingest.py` 调用处 | False | —（开=去代码块，概念类问答更干净） | — |
| `max_marginal_relevance` | `retrieve.py` | 关 | 开=结果更多样，适合宽泛问题 | — |
| `hnsw:space` | `build_index.py` | `cosine` | **别改**，OpenAI 系 embedding 就该用余弦 | — |
| `MAX_HISTORY_MESSAGES` | `rag.py` | 6 | 记更久，token 更多 | 防跑偏，短期指代易丢 |
| `temperature` | `config.py` | 0.0 | 创意场景才调高 | — |

---

*最后更新：2026年9月17日*
