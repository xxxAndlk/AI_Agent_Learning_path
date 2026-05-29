# 🤖 AI Agent 学习路径 (AI Agent Learning Path)

[![Stars](https://img.shields.io/github/stars/xxxAndlk/AI_Agent_Learning_path?style=social)](https://github.com/xxxAndlk/AI_Agent_Learning_path/stargazers)
[![Last Commit](https://img.shields.io/github/last-commit/xxxAndlk/AI_Agent_Learning_path?color=blue)](https://github.com/xxxAndlk/AI_Agent_Learning_path/commits/main)

一个专为 **Go 开发者**设计，从基础到实战、系统化学习 **AI Agent (智能体) 开发**的完整路径指南。

此项目以代码实践为核心，带你一步步掌握 Python、大语言模型 (LLM)、LangChain 框架、RAG 系统、向量数据库等前沿技术，并最终具备构建复杂 AI 应用和设计系统架构的能力。

---

## ✨ 项目特色

*   **面向 Go 开发者**：第一章即为 Python 快速入门，专门为有 Go 经验的开发者设计，学习曲线平滑。
*   **体系化结构**：从 AI 底层数学基础到上层应用开发与系统架构，形成完整的知识闭环。
*   **实战驱动**：第 12 章专设“实战项目”，提供可直接运行的完整代码。

---

## 🗺️ 学习路径大纲

整个学习路径分为 14 个章节，建议按顺序学习。

| 章节 | 目录 | 核心内容 |
| :--- | :--- | :--- |
| **1** | `1.Python快速入门（Go开发者版）` | 为 Go 开发者量身定制的 Python 速成课，快速掌握语法差异与核心特性。 |
| **2** | `2.AI底层基础` | 微积分、线性代数、概率论等入门 AI 必须掌握的数学与原理基础。 |
| **3** | `3.LLM工程基础` | 大语言模型 (LLM) 的工作原理、提示词工程、API 调用等核心概念。 |
| **4** | `4.LangChain框架详解` | 当前最流行的 LLM 应用开发框架，包括 Chains、Tools、Memory 等核心模块。 |
| **5** | `5.RAG系统（重点）` | **重点章节**。深入理解检索增强生成，学习如何为 LLM 注入外部知识。 |
| **6** | `6.Agent系统与智能体` | 智能体的核心：规划、推理与工具使用，构建能自主决策的 AI。 |
| **7** | `7.向量数据库` | 掌握 Milvus/Pinecone/Chroma 等向量数据库，理解语义搜索的基石。 |
| **8** | `8.向量数据库进阶` | 深入索引算法、性能优化、分布式部署等高级主题。 |
| **9** | `9.数据处理与特征工程` | 数据清洗、转换、Embedding 生成等为 AI 应用准备数据的关键步骤。 |
| **10** | `10.模型部署与推理优化` | 模型量化、GPU 加速、Triton 推理服务器，将模型高效部署到生产环境。 |
| **11** | `11.AI工程化与工具链` | Docker、CI/CD、MLOps、监控告警，构建可靠的 AI 系统生命全周期。 |
| **12** | `12.实战项目（完整代码）` | **理论结合实践**。包含可运行的完整 AI 应用或服务开发案例。 |
| **13** | `13.AI系统架构设计` | 学习设计高可用、可扩展的 AI 系统，如微服务化的 RAG 平台。 |
| **14** | `14.AI应用开发` | 从产品思维出发，如何设计并开发出用户体验优秀的 AI 原生应用。 |

---

## 📒 项目结构

除了核心章节，项目还包含以下辅助文件，方便你追踪内容演进：

*   `大纲.md`：项目的总体学习大纲和规划。
*   `修改记录_v4.1.md`：记录了对 LangChain 导入路径和代码块格式的重构。
*   `修改记录_v4.2.md` & `修改记录_v4.3.md`：记录了项目向 **GPT-5.4** 模型的全面升级过程。

---

## 🚀 如何开始

### 📥 1. 克隆仓库
```bash
git clone https://github.com/xxxAndlk/AI_Agent_Learning_path.git
cd AI_Agent_Learning_path

### 🐍 2. 环境准备
我们推荐使用虚拟环境隔离依赖：
```bash
python -m venv venv
source venv/bin/activate   # Windows 使用: venv\Scripts\activate
pip install -r requirements.txt   # 如果项目提供了 requirements.txt；否则各章节内会有独立的依赖说明
