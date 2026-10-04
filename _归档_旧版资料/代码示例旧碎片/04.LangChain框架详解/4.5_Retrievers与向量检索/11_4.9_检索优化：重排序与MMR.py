# retrieval_optimization.py
# 检索优化技术示例

import os
from typing import List
from langchain_community.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import CrossEncoderReranker
from langchain_core.documents import Document, BaseRetriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain.cross_encoders import HuggingFaceCrossEncoder
from langchain_openai import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "your-api-key"


def demonstrate_mmr():
    """
    MMR（最大边际相关）检索演示
    
    MMR在相关性和多样性之间取得平衡：
    - 避免返回内容高度相似的文档
    - 确保检索结果覆盖多个角度
    """
    
    from langchain.retrievers import VectorStoreRetriever
    
    # 准备语义相近但角度不同的文档
    documents = [
        Document(
            page_content="Python字典的创建方法：使用大括号dict = {}或dict()函数。",
            metadata={"source": "dict_creation", "angle": "创建方法"}
        ),
        Document(
            page_content="Python字典的操作：添加、删除、修改键值对。dict[key] = value添加，del dict[key]删除。",
            metadata={"source": "dict_operations", "angle": "操作方法"}
        ),
        Document(
            page_content="Python字典的遍历：使用for key in dict遍历所有键，使用items()方法遍历键值对。",
            metadata={"source": "dict_iteration", "angle": "遍历方法"}
        ),
        Document(
            page_content="Python字典的内部实现：使用哈希表，查找时间复杂度为O(1)。",
            metadata={"source": "dict_implementation", "angle": "实现原理"}
        ),
        Document(
            page_content="Python字典的常见错误：KeyError发生在访问不存在的键时。",
            metadata={"source": "dict_errors", "angle": "错误处理"}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="mmr_test"
    )
    
    query = "Python字典的使用方法"
    
    print(f"查询: {query}\n")
    print("=" * 60)
    
    # 1. 相似度检索（可能返回高度相似的文档）
    similarity_retriever = VectorStoreRetriever(
        vectorstore=vectorstore,
        search_type="similarity",
        search_kwargs={"k": 3}
    )
    
    print("【相似度检索】")
    results = similarity_retriever.invoke(query)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. [{doc.metadata['angle']}] {doc.page_content[:40]}...")
    
    # 2. MMR检索（保持多样性）
    mmr_retriever = VectorStoreRetriever(
        vectorstore=vectorstore,
        search_type="mmr",
        search_kwargs={
            "k": 3,                    # 最终返回数量
            "fetch_k": 20,             # 从20个候选中选择
            "lambda_mult": 0.5         # 0=最多样性, 1=最相关
        }
    )
    
    print("\n【MMR检索】")
    results = mmr_retriever.invoke(query)
    for i, doc in enumerate(results, 1):
        print(f"  {i}. [{doc.metadata['angle']}] {doc.page_content[:40]}...")
    
    # lambda_mult参数解释：
    # 0.0: 完全多样性
    # 0.5: 平衡（默认值）
    # 1.0: 完全相关性


def demonstrate_cross_encoder_rerank():
    """
    使用Cross-Encoder重排序
    
    Cross-Encoder优势：
    - 同时编码查询和文档对
    - 比Bi-Encoder更精确
    - 适合对少量候选结果精排
    """
    
    # 准备文档
    documents = [
        Document(
            page_content="机器学习是人工智能的一个分支。",
            metadata={"id": 1}
        ),
        Document(
            page_content="深度学习是机器学习的分支，使用神经网络。",
            metadata={"id": 2}
        ),
        Document(
            page_content="Python机器学习库包括Scikit-learn、TensorFlow。",
            metadata={"id": 3}
        ),
        Document(
            page_content="监督学习、无监督学习、强化学习是机器学习的类型。",
            metadata={"id": 4}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="rerank_test"
    )
    
    # 基础检索（Bi-Encoder）
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # Cross-Encoder重排序器
    # 使用HuggingFace的Cross-Encoder模型
    reranker = CrossEncoderReranker(
        cross_encoder=HuggingFaceCrossEncoder(
            model_name="BAAI/bge-reranker-base"
        ),
        top_n=2  # 重排后返回top 2
    )
    
    # 创建压缩检索器（实现重排序）
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=reranker,
        base_retriever=base_retriever
    )
    
    query = "Python机器学习库有哪些"
    
    print(f"查询: {query}\n")
    
    print("【基础检索结果】")
    results = base_retriever.invoke(query)
    for doc in results:
        print(f"  - 文档{doc.metadata['id']}: {doc.page_content}")
    
    print("\n【Cross-Encoder重排后】")
    results = compression_retriever.invoke(query)
    for doc in results:
        print(f"  - 文档{doc.metadata['id']}: {doc.page_content}")


def demonstrate_with_openai_reranker():
    """
    使用OpenAI的API进行重排序
    
    注意：需要安装langchain-openai并使用支持rerank的模型
    """
    
    from langchain_community.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import LLMChainExtractor
    
    # 这个示例演示使用LLM进行重排序的思路
    # 实际生产中可以使用专门的rerank模型
    
    print("""
    使用LLM重排序的方法：
    
    1. LLMChainExtractor：提取与查询相关的部分
    2. LLMChainFilter：过滤不相关文档
    3. 自定义重排链：让LLM对文档相关性排序
    
    示例：
    """)
    
    # 伪代码示例
    print("""
    from langchain_core.documents import Document
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI()
    
    def rerank_with_llm(query: str, documents: List[Document]) -> List[Document]:
        prompt = f"根据与查询的相关性对以下文档排序：\\n查询：{query}\\n文档："
        for i, doc in enumerate(documents):
            prompt += f"\\n{i+1}. {doc.page_content}"
        prompt += "\\n返回排序后的编号，用逗号分隔："
        
        response = llm.predict(prompt)
        # 解析响应并重新排序
        ...
    
    # 使用
    reranked = rerank_with_llm(query, documents)
    """)


def demonstrate_rerank_with_cohere():
    """
    使用Cohere进行重排序（需要API密钥）
    
    Cohere提供专门的重排序模型，效果优秀
    """
    
    print("""
    使用Cohere Rerank API：
    
    from langchain_community.retrievers import ContextualCompressionRetriever
    from langchain.retrievers.document_compressors import CohereRerank
    
    compressor = CohereRerank(
        cohere_api_key="your-api-key",
        top_n=3
    )
    
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=compressor,
        base_retriever=base_retriever
    )
    
    结果 = compression_retriever.invoke(query)
    """)


def full_optimization_pipeline():
    """
    完整的检索优化流水线
    
    阶段一：粗排（召回）
    - 使用BM25或轻量级向量检索
    - 快速从大规模文档中筛选候选集
    
    阶段二：精排（重排序）
    - 使用Cross-Encoder对候选集重排
    - 考虑查询和文档的交互
    
    阶段三：多样性处理
    - 使用MMR或DPP确保结果多样性
    - 避免信息冗余
    """
    
    print("""
    完整优化流水线示例：
    
    1. EnsembleRetriever（粗排）
       - BM25 + Vector 组合
       - RRF融合
    
    2. Cross-Encoder重排（精排）
       - BAAI/bge-reranker-base
       - Cohere rerank
    
    3. MMR多样性（后处理）
       - lambda_mult调优
    
    代码结构：
    ensemble_retriever → CrossEncoderReranker → MMR
    """)


# 运行测试
if __name__ == "__main__":
    demonstrate_mmr()
    # demonstrate_cross_encoder_rerank()
    # full_optimization_pipeline()
