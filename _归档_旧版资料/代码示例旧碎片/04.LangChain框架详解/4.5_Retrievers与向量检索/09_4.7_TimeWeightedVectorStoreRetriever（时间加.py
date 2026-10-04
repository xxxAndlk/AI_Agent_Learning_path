# time_weighted_retriever.py
# 时间加权检索器示例

import os
import time
from langchain.retrievers import TimeWeightedVectorStoreRetriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document

os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_time_weighted_retriever():
    """
    创建时间加权检索器
    
    TimeWeightedVectorStoreRetriever工作原理：
    综合考虑两个因素：
    1. 向量相似度（semantic_similarity）
    2. 时间衰减（decay_rate）
    
    得分计算：
    score = (1 - decay_rate)^(hours_elapsed) * vector_similarity
    
    适用场景：
    - 知识库经常更新
    - 需要优先展示最新内容
    - 文档有时效性要求
    """
    
    # 1. 准备文档（模拟不同时间点添加的文档）
    # 模拟旧文档
    old_doc = Document(
        page_content="Python 3.9的新特性（2020年发布）。",
        metadata={
            "source": "python39.txt",
            "last_accessed": "2024-01-01"  # 模拟访问时间
        }
    )
    
    # 模拟新文档
    new_doc = Document(
        page_content="Python 3.12的新特性（2023年发布）：性能提升。",
        metadata={
            "source": "python312.txt",
            "last_accessed": "2024-12-01"
        }
    )
    
    # 当前文档
    current_doc = Document(
        page_content="Python 3.11引入了性能改进和类型注解增强。",
        metadata={
            "source": "python311.txt",
            "last_accessed": time.strftime("%Y-%m-%d")
        }
    )
    
    documents = [old_doc, new_doc, current_doc]
    
    # 2. 创建向量数据库
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="python_versions"
    )
    
    # 3. 创建时间加权检索器
    retriever = TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore,
        # 时间衰减率：值越大，旧文档权重下降越快
        # 0表示不考虑时间，1表示完全不返回旧文档
        decay_rate=0.01,  
        # 时间衰减的计算方式：可以是天、小时等
        frequency="day",
        # 检索时是否更新访问时间
        at_least_once=True,
        # 搜索参数
        search_kwargs={"k": 3}
    )
    
    return retriever, vectorstore


def test_time_weighted_retrieval():
    """测试时间加权检索"""
    retriever, vectorstore = create_time_weighted_retriever()
    
    query = "Python新版本特性"
    
    print(f"查询: {query}\n")
    print("=" * 60)
    
    results = retriever.invoke(query)
    
    print("【时间加权检索结果】")
    print("（新文档权重更高，旧文档权重随时间衰减）\n")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.page_content}")
        print(f"   来源: {doc.metadata.get('source')}")
        print(f"   访问时间: {doc.metadata.get('last_accessed')}")
        print()


def demonstrate_decay_rate():
    """
    演示不同衰减率的影响
    """
    
    documents = [
        Document(
            page_content="旧文档内容（一年前）",
            metadata={"source": "old", "last_accessed_at": "2023-01-01"}
        ),
        Document(
            page_content="新文档内容（今天）",
            metadata={"source": "new", "last_accessed_at": "2024-12-01"}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    
    # 低衰减率（接近0）：几乎不考虑时间
    low_decay = TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore,
        decay_rate=0.00001,  # 几乎不衰减
        search_kwargs={"k": 2}
    )
    
    # 高衰减率：时间影响大
    high_decay = TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore,
        decay_rate=0.5,  # 快速衰减
        search_kwargs={"k": 2}
    )
    
    query = "文档内容"
    
    print(f"查询: {query}\n")
    
    print("【低衰减率】")
    results = low_decay.invoke(query)
    for doc in results:
        print(f"  - {doc.metadata['source']}")
    
    print("\n【高衰减率】")
    results = high_decay.invoke(query)
    for doc in results:
        print(f"  - {doc.metadata['source']}")


def semantic_and_time_combined():
    """
    语义相似度和时间权重的组合效果
    
    场景：
    - 语义上最相关的可能不是最新的
    - 时间加权在保持相关性的同时提升新文档的排名
    """
    
    # 创建语义相似但时间不同的文档
    documents = [
        Document(
            page_content="Python基础教程：变量、数据类型、控制流。适合初学者入门学习Python编程。",
            metadata={"source": "python_basic_old", "last_accessed_at": "2024-01-01"}
        ),
        Document(
            page_content="Python进阶：面向对象、异常处理、模块化编程。适合有基础的开发者。",
            metadata={"source": "python_advanced", "last_accessed_at": "2024-06-01"}
        ),
        Document(
            page_content="Python基础语法：变量声明、基本数据类型、条件语句、循环结构。",
            metadata={"source": "python_basic_new", "last_accessed_at": "2024-12-01"}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    
    query = "Python基础教程"
    
    print(f"查询: {query}\n")
    
    # 普通向量检索
    print("【普通向量检索】")
    basic_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    results = basic_retriever.invoke(query)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.metadata['source']}")
    
    # 时间加权检索
    print("\n【时间加权检索】")
    time_retriever = TimeWeightedVectorStoreRetriever(
        vectorstore=vectorstore,
        decay_rate=0.1,
        search_kwargs={"k": 3}
    )
    results = time_retriever.invoke(query)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. {doc.metadata['source']}")
    
    # 分析：
    # 向量检索：python_basic_old和python_basic_new可能相似度相同
    # 时间加权：python_basic_new会获得更高权重


# 运行测试
if __name__ == "__main__":
    test_time_weighted_retrieval()
    # demonstrate_decay_rate()
    # semantic_and_time_combined()
