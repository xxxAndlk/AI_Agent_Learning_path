# self_query_retriever.py
# 自查询检索器示例

import os
from langchain_community.retrievers import SelfQueryRetriever
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langchain.chains.query_constructor.schema import AttributeInfo

os.environ["OPENAI_API_KEY"] = "your-api-key"


def create_self_query_retriever():
    """
    创建自查询检索器
    
    SelfQueryRetriever工作原理：
    1. 使用LLM分析用户查询，提取：
       - 语义查询（要搜索的内容）
       - 元数据过滤条件
    2. 根据过滤条件筛选文档
    3. 在筛选后的文档中进行语义检索
    
    适用场景：
    - 文档有丰富的元数据（时间、作者、标签等）
    - 用户查询中包含过滤条件
    - 需要根据属性筛选文档
    """
    
    # 1. 准备带有元数据的文档
    documents = [
        # Python教程
        Document(
            page_content="Python字典是一种键值对数据结构。",
            metadata={
                "source": "python_dict.txt",
                "topic": "python",
                "level": "beginner",
                "year": 2023,
                "rating": 4.5
            }
        ),
        Document(
            page_content="Python高级特性：装饰器、生成器、上下文管理器。",
            metadata={
                "source": "python_advanced.txt",
                "topic": "python",
                "level": "advanced",
                "year": 2023,
                "rating": 4.8
            }
        ),
        # 机器学习教程
        Document(
            page_content="机器学习基础：监督学习、无监督学习。",
            metadata={
                "source": "ml_basic.txt",
                "topic": "machine_learning",
                "level": "beginner",
                "year": 2024,
                "rating": 4.6
            }
        ),
        Document(
            page_content="深度学习：神经网络、卷积神经网络、循环神经网络。",
            metadata={
                "source": "dl_advanced.txt",
                "topic": "machine_learning",
                "level": "advanced",
                "year": 2024,
                "rating": 4.7
            }
        ),
        # RAG教程
        Document(
            page_content="RAG技术简介：检索增强生成。",
            metadata={
                "source": "rag_intro.txt",
                "topic": "rag",
                "level": "intermediate",
                "year": 2024,
                "rating": 4.4
            }
        ),
        Document(
            page_content="RAG高级优化：查询扩展、重排序、混合检索。",
            metadata={
                "source": "rag_advanced.txt",
                "topic": "rag",
                "level": "advanced",
                "year": 2024,
                "rating": 4.9
            }
        ),
    ]
    
    # 2. 定义元数据字段描述（供LLM理解元数据结构）
    # 这是SelfQueryRetriever工作的关键
    metadata_field_info = [
        AttributeInfo(name="source", description="文档来源文件名", type="string"),
        AttributeInfo(name="topic", description="文档主题：python, machine_learning, rag", type="string"),
        AttributeInfo(name="level", description="难度级别：beginner, intermediate, advanced", type="string"),
        AttributeInfo(name="year", description="发布年份", type="integer"),
        AttributeInfo(name="rating", description="用户评分（1-5分）", type="float"),
    ]
    
    # 3. 创建向量数据库
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="tutorials"
    )
    
    # 4. 创建LLM
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 5. 创建SelfQueryRetriever
    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vectorstore,
        metadata_field_info=metadata_field_info,
        # 可选参数
        search_kwargs={
            "k": 5,  # 返回结果数量
            "enable_limit": True  # 允许LLM限制返回数量
        },
        # verbose=True  # 打印LLM的推理过程
    )
    
    return retriever, vectorstore


def test_self_query_retriever():
    """测试自查询检索器"""
    retriever, _ = create_self_query_retriever()
    
    test_queries = [
        "Python教程",  # 纯语义查询
        "高级难度的机器学习教程",  # 带级别过滤的查询
        "2024年发布的RAG内容",  # 带年份过滤的查询
        "评分4.5以上的Python教程",  # 带数值过滤的查询
    ]
    
    for query in test_queries:
        print(f"\n{'='*60}")
        print(f"查询: {query}")
        print("=" * 60)
        
        # LLM会自动解析出：
        # - 语义部分：在文档内容中搜索
        # - 元数据过滤：根据条件筛选
        
        results = retriever.invoke(query)
        
        print(f"\n检索到 {len(results)} 个结果:\n")
        for i, doc in enumerate(results, 1):
            print(f"{i}. {doc.page_content}")
            print(f"   主题: {doc.metadata.get('topic')}")
            print(f"   级别: {doc.metadata.get('level')}")
            print(f"   年份: {doc.metadata.get('year')}")
            print(f"   评分: {doc.metadata.get('rating')}")


def explain_query_parsing():
    """
    解释查询解析过程
    
    SelfQueryRetriever使用LLM将用户查询分解为两部分
    """
    
    print("""
    查询解析示例：
    
    用户输入: "2024年发布的Python高级教程"
    
    LLM解析为:
    - 语义查询: "Python高级教程"
    - 元数据过滤: year = 2024 AND level = "advanced" AND topic = "python"
    
    用户输入: "评分4.5以上的深度学习内容"
    
    LLM解析为:
    - 语义查询: "深度学习内容"
    - 元数据过滤: rating > 4.5 AND topic = "machine_learning"
    """)


def complex_filter_queries():
    """
    复杂过滤查询示例
    """
    
    retriever, _ = create_self_query_retriever()
    
    # 组合多个条件的查询
    complex_queries = [
        "Python或机器学习的中级教程",
        "不是2023年的高级教程",
        "评分最高的RAG内容",
    ]
    
    print("复杂过滤查询测试：\n")
    for query in complex_queries:
        print(f"查询: {query}")
        # 实际使用时会自动解析
        print("-" * 40)


def rag_with_self_query():
    """
    完整的RAG流程：使用SelfQueryRetriever
    """
    
    # 1. 准备文档（包含丰富元数据）
    documents = [
        Document(
            page_content="Python数据分析实战：使用Pandas处理数据。",
            metadata={
                "category": "data_analysis",
                "language": "python",
                "difficulty": "intermediate",
                "price": 99,
                "popularity": 8.5
            }
        ),
        Document(
            page_content="Java Web开发指南：Spring Boot入门。",
            metadata={
                "category": "web_development",
                "language": "java",
                "difficulty": "beginner",
                "price": 79,
                "popularity": 7.8
            }
        ),
    ]
    
    # 2. 创建向量数据库
    embeddings = OpenAIEmbeddings()
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        collection_name="courses"
    )
    
    # 3. 元数据字段描述
    metadata_field_info = [
        AttributeInfo(name="category", description="课程类别", type="string"),
        AttributeInfo(name="language", description="编程语言", type="string"),
        AttributeInfo(name="difficulty", description="难度：beginner/intermediate/advanced", type="string"),
        AttributeInfo(name="price", description="价格（元）", type="integer"),
        AttributeInfo(name="popularity", description="受欢迎程度（1-10）", type="float"),
    ]
    
    # 4. 创建SelfQueryRetriever
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    retriever = SelfQueryRetriever.from_llm(
        llm=llm,
        vectorstore=vectorstore,
        metadata_field_info=metadata_field_info
    )
    
    # 5. 创建问答链（v1.x：LCEL 方式，替代旧版 RetrievalQA）
    rag_prompt = ChatPromptTemplate.from_template(
        "基于以下上下文回答问题。\n\n上下文：\n{context}\n\n问题：{question}"
    )
    rag_chain = (
        {
            "context": retriever | RunnableLambda(
                lambda docs: "\n\n".join(d.page_content for d in docs)
            ),
            "question": RunnablePassthrough(),
        }
        | rag_prompt
        | llm
        | StrOutputParser()
    )
    
    # 6. 提问（包含过滤条件）
    query = "价格在100元以内的Python课程"
    answer = rag_chain.invoke(query)
    
    print(f"问题: {query}")
    print(f"回答: {answer}")


# 运行测试
if __name__ == "__main__":
    test_self_query_retriever()
    # explain_query_parsing()
    # rag_with_self_query()
