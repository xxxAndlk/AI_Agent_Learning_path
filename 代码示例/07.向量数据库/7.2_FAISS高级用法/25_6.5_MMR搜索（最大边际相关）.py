def mmr_search():
    """使用MMR（最大边际相关）进行多样性搜索"""
    
    # 准备相似文档（容易产生重复）
    docs = [
        "Python是一门易学的编程语言",
        "Python拥有丰富的库生态系统",
        "Python广泛应用于数据科学领域",
        "JavaScript是Web开发的核心语言",
        "Go语言性能优异且易于部署",
    ]
    
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_texts(docs, embeddings)
    
    # 标准相似度搜索
    print("=== 标准相似度搜索 ===")
    results = vectorstore.similarity_search("Python编程", k=3)
    for doc in results:
        print(f"  {doc.page_content}")
    
    # MMR搜索（增加多样性）
    print("\n=== MMR搜索（多样性）===")
    results_mmr = vectorstore.max_marginal_relevance_search(
        "Python编程",
        k=3,
        fetch_k=10,  # 从更多候选中选择
        lambda_mult=0.5  # 0=只关注多样性, 1=只关注相关性
    )
    for doc in results_mmr:
        print(f"  {doc.page_content}")

# mmr_search()  # 需要API密钥
