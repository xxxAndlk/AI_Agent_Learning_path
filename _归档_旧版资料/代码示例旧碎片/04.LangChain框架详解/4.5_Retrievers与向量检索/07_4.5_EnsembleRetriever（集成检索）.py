# ensemble_retriever.py
# 集成检索器示例

import os
from langchain.retrievers import EnsembleRetriever
from langchain_community.vectorstores import Chroma, FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain.retrievers import BM25Retriever
from langchain_text_splitters import CharacterTextSplitter

os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_ensemble_retriever():
    """
    创建集成检索器
    
    EnsembleRetriever工作原理：
    1. 并行运行多个检索器（BM25 + 向量检索）
    2. 对每个检索器的结果使用RRF算法融合
    3. 返回融合后的最终结果
    
    RRF (Reciprocal Rank Fusion) 算法：
    score = Σ(1 / (k + rank))
    其中k是常数（通常为60），rank是文档在各个列表中的排名
    
    适用场景：
    - 需要同时考虑关键词匹配和语义相似度
    - 单一检索器效果不理想
    - 文档中包含专业术语（BM25擅长）
    """
    
    # 1. 准备文档
    documents = [
        Document(
            page_content="Python字典是一种键值对数据结构，支持快速查找。",
            metadata={"source": "python_dict.txt", "topic": "python"}
        ),
        Document(
            page_content="Python列表是有序的元素集合，支持索引访问和切片。",
            metadata={"source": "python_list.txt", "topic": "python"}
        ),
        Document(
            page_content="机器学习使用算法从数据中学习，包括监督学习和无监督学习。",
            metadata={"source": "ml_intro.txt", "topic": "machine_learning"}
        ),
        Document(
            page_content="深度学习是机器学习的分支，使用神经网络模型。",
            metadata={"source": "dl_intro.txt", "topic": "deep_learning"}
        ),
        Document(
            page_content="Python的dict类型使用哈希表实现，查找时间复杂度为O(1)。",
            metadata={"source": "python_dict_impl.txt", "topic": "python"}
        ),
        Document(
            page_content="监督学习需要标注数据，如分类和回归任务。",
            metadata={"source": "supervised_learning.txt", "topic": "machine_learning"}
        ),
        Document(
            page_content="无监督学习不需要标注数据，如聚类和降维。",
            metadata={"source": "unsupervised_learning.txt", "topic": "machine_learning"}
        ),
    ]
    
    # 文本分割（用于BM25）
    text_splitter = CharacterTextSplitter(
        separator="。",
        chunk_size=100,
        chunk_overlap=0
    )
    split_docs = text_splitter.create_documents(
        [doc.page_content for doc in documents],
        metadatas=[doc.metadata for doc in documents]
    )
    
    # 2. 创建BM25检索器
    # BM25是一种基于关键词的传统检索算法
    # 擅长精确匹配和术语匹配
    bm25_retriever = BM25Retriever.from_documents(split_docs)
    bm25_retriever.k = 2  # 返回前2个结果
    
    # 3. 创建向量检索器
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="ensemble_docs"
    )
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    # 4. 创建集成检索器
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.5, 0.5]  # 权重可以调整
    )
    
    return ensemble_retriever, bm25_retriever, vector_retriever


def test_ensemble_retriever():
    """测试集成检索器"""
    ensemble, bm25, vector = create_ensemble_retriever()
    
    # 测试查询
    test_queries = [
        "Python字典的实现原理",
        "机器学习的类型",
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print("=" * 60)
        
        # 集成检索
        print("\n【集成检索结果】")
        ensemble_results = ensemble.invoke(query)
        for i, doc in enumerate(ensemble_results, 1):
            print(f"  {i}. {doc.page_content}")
            print(f"     来源: {doc.metadata.get('source')}")
        
        # 对比：仅BM25
        print("\n【仅BM25检索】")
        bm25_results = bm25.invoke(query)
        for i, doc in enumerate(bm25_results, 1):
            print(f"  {i}. {doc.page_content}")
        
        # 对比：仅向量检索
        print("\n【仅向量检索】")
        vector_results = vector.invoke(query)
        for i, doc in enumerate(vector_results, 1):
            print(f"  {i}. {doc.page_content}")


def explain_rrf_algorithm():
    """
    解释RRF算法
    
    RRF (Reciprocal Rank Fusion) 是一种简单的多检索器融合算法
    核心思想：综合考虑文档在不同检索结果列表中的排名
    """
    
    print("""
    RRF算法示例：
    
    假设有两个检索器返回以下结果：
    
    检索器A: [Doc1, Doc2, Doc3]
    检索器B: [Doc2, Doc1, Doc4]
    
    k=60，RRF得分计算：
    - Doc1: 1/(60+1) + 1/(60+2) = 0.0161 + 0.0161 = 0.0322
    - Doc2: 1/(60+1) + 1/(60+1) = 0.0161 + 0.0161 = 0.0322
    - Doc3: 1/(60+3) = 0.0159
    - Doc4: 1/(60+3) = 0.0159
    
    最终排序：Doc1, Doc2 > Doc3, Doc4
    
    特点：
    - 简单有效，无需训练
    - 对排名敏感的检索器效果更好
    - 可以灵活调整权重
    """)


def custom_weight_strategy():
    """
    自定义权重策略
    
    不同的查询类型可以使用不同的权重
    """
    
    documents = [
        Document(page_content="Python是一种高级语言", metadata={"id": 1}),
        Document(page_content="Java是一种强类型语言", metadata={"id": 2}),
        Document(page_content="Python有丰富的库", metadata={"id": 3}),
    ]
    
    # 创建检索器
    bm25_retriever = BM25Retriever.from_documents(documents)
    bm25_retriever.k = 3
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(documents, embeddings)
    vector_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    
    # 固定权重的集成检索器
    ensemble_fixed = EnsembleRetriever(
        retrievers=[bm25_retriever, vector_retriever],
        weights=[0.5, 0.5]
    )
    
    # 动态权重的实现思路
    # 根据查询类型调整权重
    query = "Python"
    
    print(f"查询: {query}")
    print("BM25擅长精确匹配，向量检索擅长语义匹配")
    
    # 可以在上层实现根据查询特性动态调整权重的逻辑


def advanced_ensemble():
    """
    高级用法：多检索器组合
    """
    
    # 可以组合多个不同类型的检索器
    # 例如：BM25 + 向量检索 + 关键词过滤
    
    print("""
    高级集成策略：
    
    1. 三重组合：BM25 + 向量 + 规则过滤
    2. 分层检索：粗排(BM25) + 精排(向量)
    3. 自适应权重：根据查询类型调整
    4. 重排序：在集成后加入Cross-Encoder重排
    """)


# 运行测试
if __name__ == "__main__":
    test_ensemble_retriever()
    # explain_rrf_algorithm()
