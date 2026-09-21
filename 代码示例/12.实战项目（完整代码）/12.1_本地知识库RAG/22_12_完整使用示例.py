# main.py
# RAG系统主入口
import os
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 导入配置
from config.config import Config

# 导入组件
from src.loaders.directory_loader import UnifiedDocumentLoader
from src.chunking.recursive_splitter import RecursiveTextSplitter
from src.vectorstores.faiss_store import FAISSVectorStore
from src.pipeline.rag_pipeline import RAGPipeline
from src.retrieval.query_rewriter import QueryRewriter
from src.retrieval.reranker import BGEReranker


def main():
    """主函数"""
    
    # 初始化配置
    Config.init_dirs()
    
    # 设置API Key
    os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "")
    
    # ============ 方式一：使用RAG管道 ============
    print("=" * 50)
    print("方式一：使用RAG管道")
    print("=" * 50)
    
    # 创建RAG管道
    rag = RAGPipeline(
        vector_store_type="faiss",
        llm_provider="openai",
        chunk_size=500,
        chunk_overlap=100,
        top_k=3,
        verbose=True
    )
    
    # 构建知识库
    print("\n1. 构建知识库...")
    chunks = rag.load_and_process_documents("./data/docs")
    print(f"   处理了 {len(chunks)} 个文档块")
    
    # 设置问答链
    print("\n2. 设置问答链...")
    rag.setup_qa_chain()
    
    # 问答
    print("\n3. 问答...")
    questions = [
        "什么是人工智能？",
        "机器学习和深度学习有什么区别？",
        "RAG技术有什么优势？"
    ]
    
    for q in questions:
        print(f"\n问题: {q}")
        result = rag.query(q)
        print(f"回答: {result['answer'][:200]}...")
    
    # ============ 方式二：手动构建组件 ============
    print("\n" + "=" * 50)
    print("方式二：手动构建组件")
    print("=" * 50)
    
    # 1. 加载文档
    print("\n1. 加载文档...")
    loader = UnifiedDocumentLoader()
    documents = loader.load_directory("./data/docs")
    print(f"   加载了 {len(documents)} 个文档")
    
    # 2. 文档分块
    print("\n2. 文档分块...")
    splitter = RecursiveTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(documents)
    print(f"   分割得到 {len(chunks)} 个块")
    
    # 3. 创建向量存储
    print("\n3. 创建向量存储...")
    from langchain_openai import OpenAIEmbeddings
    
    embeddings = OpenAIEmbeddings()
    vector_store = FAISSVectorStore.create_from_documents(
        documents=chunks,
        embeddings=embeddings,
        index_path="./data/processed/vectorstores/faiss_index"
    )
    print("   向量存储创建完成")
    
    # 4. 检索
    print("\n4. 检索...")
    retriever = vector_store.as_retriever(k=3)
    docs = retriever.get_relevant_documents("人工智能")
    print(f"   检索到 {len(docs)} 个相关文档")
    
    # 5. 查询重写
    print("\n5. 查询重写...")
    rewriter = QueryRewriter()
    expanded_query = rewriter.rewrite_expand("机器学习")
    print(f"   扩展查询: {expanded_query}")
    
    # 6. 重排序
    print("\n6. 重排序...")
    reranker = BGEReranker()
    reranked = reranker.rerank("机器学习", docs, top_n=2)
    print(f"   重排序后取前 {len(reranked)} 个")
    
    # 7. 生成回答
    print("\n7. 生成回答...")
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(temperature=0)
    
    context = "\n\n".join([d.page_content for d in reranked])
    prompt = f"基于以下参考文档回答问题：\n\n{context}\n\n问题：机器学习是什么？\n\n回答："
    
    answer = llm.invoke(prompt)
    print(f"   回答: {answer.content[:200]}...")
    
    print("\n" + "=" * 50)
    print("示例完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
