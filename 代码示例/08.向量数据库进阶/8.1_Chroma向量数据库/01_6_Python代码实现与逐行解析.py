# Chroma使用示例（需要安装: pip install chromadb）
"""
Chroma特点：
1. 嵌入式：无需单独部署，直接pip安装使用
2. 简单易用：API设计直观
3. 持久化：支持内存模式和磁盘持久化
4. 多模态：支持文本、图像等嵌入
5. 开源免费：Apache 2.0协议
"""

def chroma_basic_example():
    """Chroma基础使用示例"""
    try:
        import chromadb
        
        # 创建客户端
        # 方式1：内存模式（数据不持久化）
        # client = chromadb.Client()
        
        # 方式2：持久化模式（数据保存到磁盘）
        client = chromadb.PersistentClient(
            path="./chroma_db"  # 数据存储路径，自动持久化
        )  # 0.4+版本用PersistentClient替代Client+Settings
        
        # 创建或获取集合（Collection）
        # 集合类似于关系数据库中的表
        collection = client.create_collection(
            name="documents",
            metadata={"description": "文档向量存储"}
        )
        
        # 添加文档
        documents = [
            "人工智能是计算机科学的一个分支",
            "机器学习是AI的核心技术之一",
            "深度学习使用多层神经网络",
            "自然语言处理让计算机理解人类语言"
        ]
        
        ids = ["doc1", "doc2", "doc3", "doc4"]
        
        # 自动生成嵌入并添加
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=[
                {"category": "AI", "source": "wiki"},
                {"category": "ML", "source": "textbook"},
                {"category": "DL", "source": "paper"},
                {"category": "NLP", "source": "article"}
            ]
        )
        
        print(f"✅ 已添加 {len(documents)} 个文档")
        
        # 查询相似文档
        results = collection.query(
            query_texts=["什么是神经网络？"],
            n_results=2  # 返回最相似的2个
        )
        
        print("\n查询结果:")
        for i, (doc, distance) in enumerate(zip(results['documents'][0], results['distances'][0])):
            print(f"{i+1}. {doc} (距离: {distance:.4f})")
        
        # 更新文档
        collection.update(
            ids=["doc1"],
            documents=["人工智能是计算机科学的重要分支，涉及机器学习、深度学习等领域"]
        )
        print("\n✅ 文档已更新")
        
        # 删除文档
        # collection.delete(ids=["doc4"])
        
        # 获取集合统计
        count = collection.count()
        print(f"\n集合中共有 {count} 个文档")
        
        # 持久化：PersistentClient模式数据自动落盘，无需显式调用persist()
        
    except ImportError:
        print("请先安装Chroma: pip install chromadb")

def chroma_with_langchain():
    """Chroma与LangChain集成"""
    try:
        from langchain_community.vectorstores import Chroma
        from langchain_community.embeddings import OpenAIEmbeddings
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        # 准备文档
        texts = [
            "人工智能正在改变我们的生活方式",
            "机器学习算法可以从数据中学习模式",
            "深度学习在图像识别领域取得突破"
        ]
        
        # 创建向量存储
        embeddings = OpenAIEmbeddings()
        vectorstore = Chroma.from_texts(
            texts=texts,
            embedding=embeddings,
            persist_directory="./chroma_langchain"
        )
        
        # 相似性搜索
        docs = vectorstore.similarity_search("AI的应用", k=2)
        print("相似文档:")
        for doc in docs:
            print(f"- {doc.page_content}")
        
        # 持久化：langchain-chroma 0.2+由persist_directory自动落盘，无需手动调用
        
    except ImportError:
        print("请先安装依赖: pip install chromadb langchain")

if __name__ == "__main__":
    chroma_basic_example()
