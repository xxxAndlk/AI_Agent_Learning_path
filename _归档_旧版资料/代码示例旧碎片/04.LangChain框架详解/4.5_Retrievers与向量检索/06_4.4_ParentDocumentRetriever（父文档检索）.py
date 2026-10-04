# parent_document_retriever.py
# 父文档检索器示例

import os
from langchain.retrievers import ParentDocumentRetriever
from langchain_community.vectorstores import Chroma, FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain_core.documents import Document
from langchain.storage import InMemoryStore
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_parent_document_retriever():
    """
    创建父文档检索器
    
    ParentDocumentRetriever工作原理：
    1. 将长文档分成较大的父块
    2. 将父块进一步分成较小的子块
    3. 对子块进行向量索引存储
    4. 检索时，先找相关子块，再返回对应的父文档
    
    适用场景：
    - 文档较长，需要分成多个块
    - 需要同时获取局部细节和完整上下文
    - 块级别检索太细，文档级别检索太粗
    """
    
    # 1. 准备长文档（技术文档示例）
    parent_documents = [
        Document(
            page_content="""
# Python编程语言简介

Python是一种高级、解释型、面向对象的编程语言。由Guido van Rossum于1991年首次发布。

## 主要特点

1. **易于学习**：Python语法简洁明了，代码可读性高
2. **跨平台**：支持Windows、Mac、Linux等多种操作系统
3. **丰富的库**：拥有标准库和第三方库生态系统
4. **多范式**：支持面向对象、命令式、函数式编程

## 应用领域

- Web开发（Django、Flask）
- 数据科学（Pandas、NumPy）
- 机器学习（TensorFlow、PyTorch）
- 自动化脚本
- 游戏开发

## 安装Python

可以从官网python.org下载安装包，或使用包管理器（如Homebrew、conda）安装。

推荐使用虚拟环境管理项目依赖：
```bash
python -m venv myenv
source myenv/bin/activate  # Linux/Mac
myenv\\Scripts\\activate  # Windows
```

## 基本语法

Python使用缩进表示代码块，不需要大括号。变量不需要声明类型，直接赋值即可。

```python
# 变量赋值
name = "Python"
version = 3.11

# 列表
numbers = [1, 2, 3, 4, 5]

# 字典
person = {"name": "张三", "age": 25}

# 条件语句
if version >= 3:
    print("使用Python 3")
```
            """,
            metadata={"source": "python_tutorial.txt", "type": "教程", "topic": "python"}
        ),
        Document(
            page_content="""
# 机器学习基础

机器学习是人工智能的一个分支，专注于让计算机从数据中学习并做出预测或决策。

## 什么是机器学习

机器学习是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。它使计算机能够从数据中学习，而不需要被明确编程。

## 机器学习类型

### 1. 监督学习
从标注好的训练数据中学习，包括：
- **分类**：预测离散标签（如垃圾邮件检测）
- **回归**：预测连续值（如房价预测）

### 2. 无监督学习
从无标签数据中学习，包括：
- **聚类**：将相似数据分组（如客户分群）
- **降维**：减少特征数量（如PCA）

### 3. 强化学习
通过与环境交互学习最优策略（如游戏AI）

## 常用算法

- 线性回归：用于回归任务
- 逻辑回归：用于二分类
- 决策树：可解释性强
- 随机森林：集成学习方法
- 支持向量机：适合高维数据
- 神经网络：深度学习基础

## 学习路线

推荐学习路线：
1. Python基础
2. NumPy和Pandas数据处理
3. Scikit-learn机器学习库
4. 深度学习框架（TensorFlow/PyTorch）
            """,
            metadata={"source": "ml_tutorial.txt", "type": "教程", "topic": "machine_learning"}
        ),
        Document(
            page_content="""
# RAG技术详解

RAG（Retrieval-Augmented Generation，检索增强生成）是一种结合检索和生成的AI技术架构。

## 为什么需要RAG

大语言模型存在以下局限：
- **知识截止**：训练数据有时效性，无法获取最新信息
- **幻觉问题**：可能生成不准确的信息
- **专业知识不足**：对特定领域了解有限
- **长尾知识**：对低频信息记忆不完整

RAG通过检索外部知识库来增强LLM的生成能力，有效解决上述问题。

## RAG工作流程

1. **文档处理**：加载、分割、向量化文档
2. **查询处理**：将用户查询向量化
3. **相似度检索**：从向量数据库中检索相关文档
4. **上下文增强**：将检索结果作为Prompt上下文
5. **生成回答**：LLM基于上下文生成回答

## RAG优化技术

- **分块策略**：选择合适的chunk_size和重叠
- **向量模型**：选择效果好的embedding模型
- **混合检索**：结合关键词和向量检索
- **重排序**：使用Cross-Encoder重排结果
- **查询扩展**：使用LLM生成多个查询变体
- **上下文压缩**：提取关键信息，减少噪音

## 工具选择

- 向量数据库：Chroma、FAISS、Milvus、Qdrant、Pinecone
- Embedding：OpenAI、BAAI、HuggingFace
- 框架：LangChain、LlamaIndex
            """,
            metadata={"source": "rag_tutorial.txt", "type": "教程", "topic": "rag"}
        ),
    ]
    
    # 2. 创建向量数据库（用于子块检索）
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=[],  # 稍后添加子块
        embedding=embeddings,
        collection_name="child_documents"
    )
    
    # 3. 创建父文档存储
    # 方式一：内存存储（适合小规模）
    docstore = InMemoryStore()
    
    # 方式二：文件存储（适合大规模）
    # from langchain.storage import FileStore
    # docstore = FileStore("./parent_docs")
    
    # 4. 创建文本分割器
    
    # 父文档分割器：将长文档分成较大的块
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # 父文档块大小
        chunk_overlap=100,
        separators=["\n\n", "\n", "。", ".", " "]
    )
    
    # 子文档分割器：将父文档分成更小的块用于检索
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,   # 子块大小（更小，更精细的检索）
        chunk_overlap=20,
        separators=["\n\n", "\n", "。", ".", " "]
    )
    
    # 5. 创建ParentDocumentRetriever
    retriever = ParentDocumentRetriever(
        vectorstore=vectorstore,
        docstore=docstore,
        child_splitter=child_splitter,
        parent_splitter=parent_splitter,
        # 可选参数
        search_kwargs={"k": 5}  # 检索的子块数量
    )
    
    # 6. 添加文档（会自动分割并建立索引）
    retriever.add_documents(parent_documents)
    
    return retriever, vectorstore


def test_parent_document_retriever():
    """测试父文档检索器"""
    retriever, vectorstore = create_parent_document_retriever()
    
    # 测试查询
    test_queries = [
        "Python有哪些特点？",
        "机器学习有哪些类型？",
        "RAG如何优化检索效果？"
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print("=" * 60)
        
        results = retriever.invoke(query)
        
        print(f"\n检索到 {len(results)} 个文档:\n")
        for i, doc in enumerate(results, 1):
            print(f"文档 {i} (长度: {len(doc.page_content)} 字符):")
            # 打印前200个字符
            content = doc.page_content[:200].replace("\n", " ")
            print(f"  {content}...")
            print(f"  来源: {doc.metadata.get('source')}")
            print()


def compare_with_child_only():
    """
    对比：仅使用子块检索 vs 父文档检索
    """
    # 创建向量数据库
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=[
            Document(
                page_content="Python是一种高级编程语言，具有易于学习、跨平台、库丰富等特点。",
                metadata={"source": "doc1"}
            ),
            Document(
                page_content="Python应用于Web开发、数据科学、机器学习等领域。Django和Flask是常用的Web框架。",
                metadata={"source": "doc2"}
            ),
            Document(
                page_content="机器学习是AI的一个分支，包括监督学习、无监督学习、强化学习等类型。",
                metadata={"source": "doc3"}
            ),
        ],
        embedding=embeddings
    )
    
    query = "Python在机器学习中的应用"
    
    # 仅子块检索
    child_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    child_results = child_retriever.invoke(query)
    
    print("【仅子块检索】")
    for doc in child_results:
        print(f"  - {doc.page_content}")
    
    # 父文档检索（需要额外配置）
    # parent_retriever = ParentDocumentRetriever(...)
    # parent_results = parent_retriever.invoke(query)
    
    print("\n【父文档检索优势】")
    print("  - 返回完整上下文而非碎片化信息")
    print("  - 保留文档的结构和连贯性")
    print("  - LLM可以更好地理解整体内容")


def advanced_parent_retriever():
    """
    高级配置：使用不同的文档存储
    """
    
    from langchain.storage import RedisStore, ElasticsearchStore
    
    # Redis存储（适合分布式场景）
    # docstore = RedisStore(
    #     redis_url="redis://localhost:6379",
    #     key_prefix="parent_docs"
    # )
    
    # Elasticsearch存储（适合大规模）
    # docstore = ElasticsearchStore(
    #     index_name="parent_docs",
    #     es_url="http://localhost:9200"
    # )
    
    print("高级存储配置示例")


# 运行测试
if __name__ == "__main__":
    test_parent_document_retriever()
    # compare_with_child_only()
