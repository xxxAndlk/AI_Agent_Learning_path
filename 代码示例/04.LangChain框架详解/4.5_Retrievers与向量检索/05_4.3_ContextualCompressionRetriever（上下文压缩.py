# contextual_compression_retriever.py
# 上下文压缩检索器示例

import os
from langchain_community.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor, LLMChainFilter
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_text_splitters import CharacterTextSplitter

os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_compression_retriever():
    """
    创建上下文压缩检索器
    
    ContextualCompressionRetriever工作原理：
    1. 使用基础检索器检索候选文档
    2. 使用LLM从每个候选文档中提取相关内容
    3. 返回压缩后的相关片段
    
    适用场景：
    - 文档较长，包含大量无关内容
    - 需要精确的上下文片段
    - 上下文窗口有限，需要压缩
    """
    
    # 1. 准备长文档（包含大量无关内容）
    long_document = """
    Python是一种广泛使用的解释型、高级和通用的编程语言。
    Python支持多种编程范式，包括结构化、过程式、反射式、面向对象和函数式编程。
    它拥有动态类型系统和垃圾回收功能，能够自动管理内存使用。
    
    == 这里是中间的一大段无关内容 ==
    Python的设计哲学强调代码的可读性和简洁的语法（尤其是使用空格缩进划分代码块，
    而非使用大括号或关键词）。相比C++或Java，Python让开发者能够用更少的代码
    表达想法。不管是小型还是大型程序，该语言都试图让程序的结构清晰明了。
    
    与Scheme、Ruby、Perl、Tcl等动态类型语言一样，Python拥有动态类型和垃圾回收功能，
    能够自动管理内存使用，并且支持多种编程范式，包括面向对象、命令式、函数式和过程式编程。
    
    == 又是一些背景介绍 ==
    Python在各个领域都有广泛应用，包括Web开发、数据分析、人工智能、科学计算等。
    Python的标准库非常丰富，被称为"batteries included"，这意味着开箱即用。
    常见的Web框架有Django、Flask、Tornado等。
    数据处理库有Pandas、NumPy、Matplotlib等。
    机器学习库有TensorFlow、PyTorch、Scikit-learn等。
    
    具体来说，Python的字典（dict）是一种键值对数据结构，提供O(1)时间复杂度的查找。
    可以使用大括号{}或dict()函数创建字典。字典的常见操作包括：
    1. 添加键值对：dict[key] = value
    2. 获取值：dict.get(key)
    3. 删除键值对：del dict[key]
    4. 获取所有键：dict.keys()
    5. 获取所有值：dict.values()
    
    == 更多无关内容 ==
    Python的创始人Guido van Rossum在1991年首次发布了Python。Python这个名字
    并不是来自蛇，而是来自Guido喜欢的喜剧团体Monty Python。
    Python的版本演进：Python 1.0于1994年发布，Python 2.0于2000年发布，
    Python 3.0于2008年发布。2020年，Python 2停止维护。
    """ * 3  # 重复3次使文档更长
    
    # 2. 分割文档
    text_splitter = CharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separator="\n"
    )
    documents = text_splitter.create_documents(
        texts=[long_document],
        metadatas=[{"source": "python_guide.txt", "topic": "Python"}]
    )
    
    print(f"文档被分成 {len(documents)} 个块\n")
    
    # 3. 创建向量数据库
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="long_docs"
    )
    
    # 4. 创建基础检索器
    base_retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )
    
    # 5. 创建LLM
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 6. 创建文档压缩器
    
    # 方式一：LLMChainExtractor（提取与查询相关的部分）
    # 这是最常用的压缩器，会让LLM判断每个文档块中与查询相关的部分
    extractor = LLMChainExtractor.from_llm(llm)
    
    # 方式二：LLMChainFilter（过滤掉不相关的文档）
    # 只保留相关文档，不做内容提取
    # filter_compressor = LLMChainFilter.from_llm(llm)
    
    # 7. 创建压缩检索器
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=extractor,
        base_retriever=base_retriever
    )
    
    return compression_retriever, vectorstore, base_retriever


def test_contextual_compression():
    """测试上下文压缩检索"""
    compression_retriever, vectorstore, base_retriever = create_compression_retriever()
    
    query = "Python字典如何创建和使用？"
    
    print(f"查询: {query}\n")
    print("=" * 60)
    
    # 基础检索结果
    print("【基础检索结果】(原始文档块)")
    base_results = base_retriever.invoke(query)
    for i, doc in enumerate(base_results, 1):
        print(f"\n块 {i} (长度: {len(doc.page_content)} 字符):")
        print(f"  {doc.page_content[:200]}...")
    
    print("\n" + "=" * 60)
    print("【压缩检索结果】(提取的相关内容)")
    
    # 压缩检索结果
    compression_results = compression_retriever.invoke(query)
    for i, doc in enumerate(compression_results, 1):
        print(f"\n结果 {i} (长度: {len(doc.page_content)} 字符):")
        print(f"  {doc.page_content}")


def different_compression_methods():
    """
    不同的压缩方法对比
    """
    
    # 准备测试文档
    documents = [
        Document(
            page_content="""
            # Python教程
            
            Python是一种高级编程语言。本教程介绍Python的基础知识。
            变量不需要声明类型，直接赋值即可。
            列表是Python中最常用的数据结构之一。
            
            ## 字符串操作
            Python字符串支持多种操作：切片、连接、格式化。
            f-string是Python 3.6引入的字符串格式化方式。
            """,
            metadata={"source": "python_tutorial.txt"}
        ),
        Document(
            page_content="""
            # JavaScript教程
            
            JavaScript是一种用于Web开发的脚本语言。
            变量使用var、let、const声明。
            数组是JavaScript中的重要数据结构。
            
            ## 字符串操作
            JavaScript字符串使用+号连接或模板字符串。
            ES6引入了模板字符串语法。
            """,
            metadata={"source": "js_tutorial.txt"}
        ),
        Document(
            page_content="""
            # Python进阶
            
            深入理解Python的内部机制。
            Python的字典使用哈希表实现，查找效率高。
            列表推导式是Python特有的语法糖。
            
            ## 性能优化
            使用生成器可以节省内存。
            使用itertools模块处理迭代操作。
            """,
            metadata={"source": "python_advanced.txt"}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="tutorials"
    )
    
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    query = "Python字符串如何格式化？"
    
    print(f"查询: {query}\n")
    
    # 1. LLMChainExtractor - 提取相关内容
    extractor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=extractor,
        base_retriever=base_retriever
    )
    
    print("【LLMChainExtractor】提取相关内容片段")
    results = compression_retriever.invoke(query)
    for doc in results:
        print(f"  - {doc.page_content[:150]}...")
    
    # 2. LLMChainFilter - 过滤不相关文档
    filter_compressor = LLMChainFilter.from_llm(llm)
    filter_retriever = ContextualCompressionRetriever(
        base_compressor=filter_compressor,
        base_retriever=base_retriever
    )
    
    print("\n【LLMChainFilter】过滤掉不相关文档")
    results = filter_retriever.invoke(query)
    for doc in results:
        print(f"  - {doc.page_content[:150]}...")
    
    # 3. 不使用压缩（基准对比）
    print("\n【无压缩】返回原始文档块")
    results = base_retriever.invoke(query)
    for doc in results:
        print(f"  - {doc.page_content[:150]}...")


def embed_documents_compressor():
    """
    使用Embedding过滤器的压缩器
    
    EmbeddingsFilter根据文档与查询的Embedding相似度来过滤文档
    相比LLMChainFilter，速度更快成本更低（不需要调用LLM）
    """
    
    from langchain.retrievers.document_compressors import EmbeddingsFilter
    
    documents = [
        Document(page_content="Python字典：键值对存储，O(1)查找", metadata={"id": 1}),
        Document(page_content="JavaScript数组：有序集合，索引访问", metadata={"id": 2}),
        Document(page_content="Python列表推导式：简洁创建列表", metadata={"id": 3}),
        Document(page_content="Python元组：不可变序列", metadata={"id": 4}),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="embed_filter"
    )
    
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 4})
    
    # 创建基于Embedding的过滤器
    # 保留相似度超过阈值的文档
    embeddings_filter = EmbeddingsFilter(
        embeddings=embeddings,
        similarity_threshold=0.5
    )
    
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=embeddings_filter,
        base_retriever=base_retriever
    )
    
    query = "Python的数据结构"
    print(f"查询: {query}\n")
    
    results = compression_retriever.invoke(query)
    for doc in results:
        print(f"  - {doc.page_content} (ID: {doc.metadata['id']})")


def rag_with_compression():
    """
    完整的RAG流程：使用上下文压缩检索
    """
    
    # 1. 准备文档
    docs = [
        Document(
            page_content="""Python机器学习库包括：
            - Scikit-learn: 传统机器学习
            - TensorFlow: 深度学习框架
            - PyTorch: 深度学习框架
            - Pandas: 数据处理
            - NumPy: 数值计算
            本教程介绍Scikit-learn的基本使用方法。
            """,
            metadata={"source": "ml_libs.txt"}
        ),
        Document(
            page_content="""深度学习是机器学习的一个分支，使用神经网络。
            常见的神经网络类型包括：
            - CNN: 卷积神经网络，用于图像处理
            - RNN: 循环神经网络，用于序列数据
            - Transformer: 注意力机制，广泛应用于NLP
            本节介绍CNN的基本原理。
            """,
            metadata={"source": "dl_intro.txt"}
        ),
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        collection_name="ml_docs"
    )
    
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 2. 创建压缩检索器
    base_retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    extractor = LLMChainExtractor.from_llm(llm)
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=extractor,
        base_retriever=base_retriever
    )
    
    # 3. 创建问答链（v1.x：LCEL 方式，替代旧版 RetrievalQA）
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_prompt = ChatPromptTemplate.from_template(
        "基于以下上下文回答问题。\n\n上下文：\n{context}\n\n问题：{question}"
    )
    rag_chain = (
        {"context": compression_retriever | format_docs, "question": RunnablePassthrough()}
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    
    # 4. 提问
    query = "Python有哪些机器学习库？"
    answer = rag_chain.invoke(query)
    
    print(f"问题: {query}\n")
    print(f"回答: {answer}\n")
    print("使用的源文档:")
    for doc in compression_retriever.invoke(query):
        print(f"  - {doc.page_content[:100]}...")


# 运行测试
if __name__ == "__main__":
    test_contextual_compression()
    # different_compression_methods()
    # embed_documents_compressor()
    # rag_with_compression()
