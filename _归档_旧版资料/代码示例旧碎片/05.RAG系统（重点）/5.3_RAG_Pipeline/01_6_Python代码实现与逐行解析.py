# 导入LangChain核心组件，构建完整的RAG Pipeline
# FAISS: Facebook AI Similarity Search，高效的向量相似度搜索库
from langchain_community.vectorstores import FAISS
# OpenAIEmbeddings: OpenAI的文本嵌入模型，将文本转为向量
from langchain_openai import OpenAIEmbeddings
# RecursiveCharacterTextSplitter: 递归文本分割器，保持语义完整性
from langchain_text_splitters import RecursiveCharacterTextSplitter
# TextLoader: 文本文件加载器
from langchain_community.document_loaders import TextLoader
# 检索问答链RetrievalQA等已迁移至langchain-classic；新版推荐用LCEL组合，见第7步
# ChatOpenAI: OpenAI的聊天大语言模型接口
from langchain_openai import ChatOpenAI
# 用于构建RAG Prompt
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

def rag_pipeline_example():
    """
    完整的RAG流程示例
    
    RAG = Retrieval + Generation
    完整的流程包含7个步骤：
    1. 加载文档 -> 2. 分块 -> 3. 生成Embedding -> 4. 存储到向量库
    5. 检索相关文档 -> 6. 构建Prompt -> 7. LLM生成回答
    """
    
    # 1. 加载文档
    # 使用TextLoader加载example.txt文件，指定UTF-8编码
    # loader.load()返回Document对象列表，每个Document包含page_content和metadata
    loader = TextLoader("example.txt", encoding="utf-8")
    documents = loader.load()
    
    # 2. 文档分块
    # 使用RecursiveCharacterTextSplitter将长文档切分成小块
    # 参数说明：
    # - chunk_size=100: 每块100字符，平衡语义完整性和检索精度
    # - chunk_overlap=20: 相邻块重叠20字符，保持上下文连贯性
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100,               # 每块100字符
        chunk_overlap=20              # 重叠20字符
    )
    # 执行分块，返回分块后的Document列表
    texts = text_splitter.split_documents(documents)
    
    # 3. 生成Embedding并存储到FAISS
    # 创建OpenAI的Embedding模型实例
    # OpenAIEmbeddings使用text-embedding-3-small模型（默认）
    # 模型会将文本转换为1536维的向量表示
    embeddings = OpenAIEmbeddings()
    # FAISS.from_documents()方法完成两件事：
    # 1) 将所有文本块通过Embedding模型转换为向量
    # 2) 将向量和原始文本存储到FAISS向量数据库中
    # 返回的db对象是FAISS向量数据库实例，支持相似度检索
    db = FAISS.from_documents(texts, embeddings)
    
    # 4. 创建检索器
    # as_retriever()将向量数据库转换为检索器接口
    # search_kwargs={"k": 3}表示检索最相似的3个文档
    # 这是RAG的标准配置：先召回相关文档，再送入LLM生成
    retriever = db.as_retriever(search_kwargs={"k": 3})
    
    # 5. 初始化LLM
    # 创建ChatOpenAI实例（推荐使用Chat模型）
    # temperature=0使输出更确定性、减少随机性，适合问答场景
    llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 6. 定义RAG Prompt模板
    prompt = ChatPromptTemplate.from_template("""
基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文：
{context}

问题：
{question}

请提供详细且准确的答案：
""")
    
    # 7. 使用LCEL组合RAG链（新版推荐方式）
    # 检索上下文并与问题一起传入Prompt
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])
    
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    # 8. 执行问答
    query = "这段文本主要讲了什么？"
    # invoke()执行完整RAG流程
    answer = rag_chain.invoke(query)
    
    # 获取源文档
    source_docs = retriever.invoke(query)
    
    # 打印结果
    print("RAG回答:", answer)
    print("源文档数量:", len(source_docs))

# 程序入口
if __name__ == "__main__":
    rag_pipeline_example()
