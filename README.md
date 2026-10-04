# 🤖 AI Agent 学习路径

[![Stars](https://img.shields.io/github/stars/xxxAndlk/AI_Agent_Learning_path?style=social)](https://github.com/xxxAndlk/AI_Agent_Learning_path/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/xxxAndlk/AI_Agent_Learning_path?color=blue)](https://github.com/xxxAndlk/AI_Agent_Learning_path/commits/main)

一条从 **完全零基础** 到能独立开发 **AI Agent（智能体）应用** 的系统学习路径，全程使用 Python。

## 👉 第一次来？从这里开始

1. **先读 [`新手使用指南.md`](新手使用指南.md)**：5 分钟搞懂要准备什么、API Key 怎么弄、常见报错怎么办。
2. **跑一次环境自检**（不用先装任何东西）：
   ```bash
   python check_env.py
   ```
3. **打开第 1 章**：[`01.Python快速入门/课程大纲.md`](01.Python快速入门/课程大纲.md)，边看边敲每段代码。

> 不会装环境？Windows 双击 `setup.bat`、Mac/Linux 执行 `bash setup.sh`，可一键创建虚拟环境、安装依赖并自检。

## ✨ 项目特点

- **真正零基础**：第 1 章从"什么是 Python"讲起，用大白话和生活类比，不预设任何编程基础。
- **讲课式讲义**：每课含直觉引入、示意图（Mermaid）、动手代码、"想一想"和"小结"，不是冷冰冰的参考手册。
- **离线也能练**：大量配套脚本用 Python 标准库即可运行；需要调用大模型的部分会明确标注"需 API Key"。
- **体系完整**：Python → AI 原理 → 调用大模型 → LangChain → RAG → Agent → 向量数据库 → 实战与架构。

## 🗺️ 学习路线（14 章）

| 章 | 主题 | 内容 | 状态 |
|:-:|------|------|:--:|
| 1 | Python 快速入门 | 12 课零基础 Python（变量、函数、文件、OOP、并发…） | ✅ 新课 |
| 2 | AI 底层基础 | 9 课 + 1 加餐：AI/机器学习/神经网络/Transformer 直觉 | ✅ 新课 |
| 3 | LLM 工程基础 | 4 课：第一次调用、Prompt、Function Calling、结构化输出 | ✅ 新课 |
| 4 | LangChain 框架 | 7 课：架构、LCEL、记忆、工具与 Agent、检索、解析、实战 | ✅ 新课 |
| 5 | RAG 系统（重点） | 6 课：全景、切块、Embedding、流水线、高级主题、重排 | ✅ 新课 |
| 6 | Agent 系统与智能体 | 智能体循环、记忆、安全、LangGraph、MCP、多 Agent | ✅ 新课 |
| 7 | 向量数据库 | FAISS 索引与检索 | ✅ 新课 |
| 8 | 向量数据库进阶 | Chroma、Milvus、PGVector、索引算法与选型 | ✅ 新课 |
| 9 | 数据处理与特征工程 | 清洗、特征、数据增强、LLM 数据工程 | ✅ 新课 |
| 10 | 模型部署与推理优化 | 导出、量化、推理框架、服务化 | ✅ 新课 |
| 11 | AI 工程化与工具链 | 实验追踪、版本、监控、可观测性、LLM 评测 | ✅ 新课 |
| 12 | 实战项目 | 知识库 RAG、Agent 系统、客服、多 Agent 等完整项目 | ✅ 新课 |
| 13 | AI 系统架构设计 | LLM / RAG / Agent / MCP / SaaS 架构 | ✅ 新课 |
| 14 | AI 应用开发 | FastAPI、聊天应用、Streamlit/Gradio、插件系统 | ✅ 新课 |

> 状态说明：本项目已完成从"技术参考文档"到"零基础系统课程"的整体重制，**14 章共 83 课全部为新课**；每课含讲义 .md 和可运行的 .py，原版资料留存于 `_归档_旧版资料/` 供查阅。

## ⚙️ 环境与依赖

- 第 1 章：**零依赖**，装好 Python 即可。
- 第 3 章起：执行 `pip install openai python-dotenv`，并配置 API Key（见新手指南第四节）。
- 全书依赖汇总在 [`requirements.txt`](requirements.txt)（按需安装，不必一次全装）；配置模板见 [`.env.example`](.env.example)。

## 📁 项目结构

```text
01~14 章/                 每章含《课程大纲.md》和若干「第XX课_主题/」
                          每个课次目录里有讲义 .md 和可运行的 .py
新手使用指南.md           零基础入门说明（术语表 / Key 申请 / 常见报错）
check_env.py              环境自检脚本（纯标准库）
requirements.txt          全书依赖清单
.env.example              环境变量模板（复制为 .env 后填 Key）
setup.bat / setup.sh      一键环境准备（Windows / Mac·Linux）
新手引导图/               安装关键步骤的示意标注图（配合新手指南第二节）
_归档_旧版资料/           已被新课取代的旧文档与旧代码示例，主线学习可忽略
修改记录_v4.5.md          版本修改记录
```

## 📝 说明

- 所有需要联网调用大模型的代码，API Key 一律从环境变量或 `.env` 读取，**请勿把 Key 写进代码或提交到 git**（`.env` 已被 `.gitignore` 忽略）。
- AI 工具链更新很快，讲义中涉及具体型号/版本处会标注"以官方文档为准"。

---

祝你学习愉快，动手做出第一个属于自己的 AI 应用！
