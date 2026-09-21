# multi_query_retriever.py
# 多查询检索器示例

import os
from langchain.retrievers import MultiQueryRetriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import List

os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_multi_query_retriever():
    """
    创建多查询检索器
    
    MultiQueryRetriever工作原理：
    1. 使用LLM根据原始查询生成3-5个不同的查询表述
    2. 对每个查询进行向量检索
    3. 合并所有结果并去重
    4. 返回合并后的文档列表
    
    适用场景：
    - 用户查询表达方式多样
    - 文档内容与查询表述存在差异
    - 需要提高检索召回率
    """
    
    # 1. 准备文档
    documents = [
        Document(
            page_content="Python的字典是一种键值对的数据结构，支持快速查找。",
            metadata={"source": "dict_guide.txt", "topic": "Python"}
        ),
        Document(
            page_content="在Python中，可以使用大括号或dict()函数创建字典。",
            metadata={"source": "dict_creation.txt", "topic": "Python"}
        ),
        Document(
            page_content="字典的常见操作包括：添加、删除、修改和查询键值对。",
            metadata={"source": "dict_operations.txt", "topic": "Python"}
        ),
        Document(
            page_content="Python列表是有序的元素集合，支持索引访问。",
            metadata={"source": "list_guide.txt", "topic": "Python"}
        ),
        Document(
            page_content="列表推导式是Python中创建列表的简洁方式。",
            metadata={"source": "list_comprehension.txt", "topic": "Python"}
        ),
        Document(
            page_content="集合（Set）是Python中无序且不重复的元素集合。",
            metadata={"source": "set_guide.txt", "topic": "Python"}
        ),
    ]
    
    # 2. 创建向量数据库
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="python_docs"
    )
    
    # 3. 创建LLM
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 4. 自定义查询生成提示词（可选）
    # 默认提示词会生成3个查询变体
    QUERY_PROMPT = PromptTemplate(
        input_variables=["question"],
        template="""您是一个AI助手。用户提出了一个问题，请生成3个不同的查询来检索相关文档。
        每个查询应该从不同角度表达原始问题。
        
        原始问题: {question}
        
        生成的不同查询（每行一个）:
        """
    )
    
    # 5. 创建MultiQueryRetriever
    retriever = MultiQueryRetriever(
        retriever=vectorstore.as_retriever(search_kwargs={"k": 2}),
        llm=llm,
        prompt=QUERY_PROMPT,  # 可选，自定义提示词
        # verbose=True  # 打印生成的查询
    )
    
    return retriever, vectorstore


def test_multi_query_retriever():
    """测试多查询检索器"""
    retriever, _ = create_multi_query_retriever()
    
    # 这个查询使用"字典"这个词，但文档中没有直接使用这个词
    # MultiQueryRetriever会生成"dict"、"键值对"等变体查询
    query = "Python中如何存储键值对数据？"
    
    print(f"原始查询: {query}\n")
    print("=" * 60)
    
    # 由于MultiQueryRetriever会调用LLM，这里我们模拟演示
    # 实际使用时retriever.invoke(query)会打印生成的查询
    
    results = retriever.invoke(query)
    
    print(f"\n检索到 {len(results)} 个结果:\n")
    for i, doc in enumerate(results, 1):
        print(f"{i}. {doc.page_content}")
        print(f"   来源: {doc.metadata.get('source')}")
        print()


def compare_single_vs_multi():
    """对比单查询和多查询检索效果"""
    documents = [
        Document(
            page_content="如何使用Python字典进行数据存储？字典提供快速的键值对查找。",
            metadata={"id": 1}
        ),
        Document(
            page_content="Python的dict类型是哈希表实现，查找时间复杂度为O(1)。",
            metadata={"id": 2}
        ),
        Document(
            page_content="列表推导式是Python独特的语法，可以简洁地创建新列表。",
            metadata={"id": 3}
        ),
        Document(
            page_content="集合Set用于存储不重复的元素，支持交并差运算。",
            metadata={"id": 4}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="test_collection"
    )
    
    # 单查询检索
    single_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    
    # 多查询检索（使用LLM生成变体）
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    multi_retriever = MultiQueryRetriever(
        retriever=single_retriever,
        llm=llm,
        verbose=False
    )
    
    # 测试查询：涉及"哈希表"概念，文档中没有直接提及
    query = "Python中使用哈希表存储数据的方法"
    
    print(f"查询: {query}\n")
    
    print("【单查询检索结果】")
    single_results = single_retriever.invoke(query)
    for doc in single_results:
        print(f"  - 文档{doc.metadata['id']}: {doc.page_content[:30]}...")
    
    print("\n【多查询检索结果】")
    # 注意：实际调用会生成新的查询，这里演示合并效果
    multi_results = multi_retriever.invoke(query)
    for doc in multi_results:
        print(f"  - 文档{doc.metadata['id']}: {doc.page_content[:30]}...")


def custom_query_generator():
    """
    自定义查询生成逻辑
    
    可以继承MultiQueryRetriever或直接实现自定义逻辑
    """
    
    from langchain.retrievers.multi_query import LineListOutputParser
    from langchain.output_parsers import CommaSeparatedListOutputParser
    
    # 使用不同的输出解析器
    # CommaSeparatedListOutputParser: 逗号分隔的列表
    
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 自定义链：生成查询 → 解析为列表
    llm_chain = (
        PromptTemplate(
            input_variables=["question"],
            template="为这个问题生成3个不同的查询: {question}"
        )
        | llm
        | CommaSeparatedListOutputParser()
    )
    
    # 这个自定义chain可以传给MultiQueryRetriever
    # retriever = MultiQueryRetriever(...)
    
    print("自定义查询生成链已创建")


def advanced_multi_query_with_filters():
    """
    高级用法：结合元数据过滤
    
    MultiQueryRetriever可以与过滤功能结合使用
    """
    
    # 创建带主题标签的文档
    documents = [
        Document(
            page_content="Python字典详解：键值对存储",
            metadata={"topic": "python", "level": "beginner"}
        ),
        Document(
            page_content="Python列表操作指南",
            metadata={"topic": "python", "level": "beginner"}
        ),
        Document(
            page_content="深度学习中的哈希技术",
            metadata={"topic": "deep_learning", "level": "advanced"}
        ),
        Document(
            page_content="机器学习基础：数据结构",
            metadata={"topic": "machine_learning", "level": "intermediate"}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="filter_test"
    )
    
    # 创建带过滤的基础检索器
    base_retriever = vectorstore.as_retriever(
        search_kwargs={
            "k": 2,
            "filter": {"topic": "python"}  # 只检索Python相关文档
        }
    )
    
    # 创建多查询检索器
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    multi_retriever = MultiQueryRetriever(
        retriever=base_retriever,
        llm=llm,
        verbose=False
    )
    
    query = "数据结构存储方式"
    print(f"查询: {query}")
    print("过滤: topic = 'python'\n")
    
    results = multi_retriever.invoke(query)
    for doc in results:
        print(f"  - {doc.page_content}")
        print(f"    标签: {doc.metadata}")
        print()


# 运行测试
if __name__ == "__main__":
    test_multi_query_retriever()
    # compare_single_vs_multi()
    # advanced_multi_query_with_filters()
