def metadata_filtering():
    """元数据过滤详解"""
    
    import chromadb
    
    client = chromadb.PersistentClient(
        path="./metadata_demo"
    )
    
    collection = client.get_or_create_collection(
        name="products"
    )
    
    # 添加示例数据
    products = [
        "iPhone 15 Pro Max",
        "Samsung Galaxy S24",
        "MacBook Pro M3",
        "Dell XPS 15",
        "Sony WH-1000XM5"
    ]
    
    ids = ["p1", "p2", "p3", "p4", "p5"]
    
    metadatas = [
        {"category": "手机", "brand": "Apple", "price": 9999, "in_stock": True},
        {"category": "手机", "brand": "Samsung", "price": 6999, "in_stock": True},
        {"category": "笔记本", "brand": "Apple", "price": 19999, "in_stock": False},
        {"category": "笔记本", "brand": "Dell", "price": 12999, "in_stock": True},
        {"category": "耳机", "brand": "Sony", "price": 2699, "in_stock": True},
    ]
    
    collection.add(
        documents=products,
        ids=ids,
        metadatas=metadatas
    )
    
    # ============ 精确匹配过滤 ============
    # 查询品牌为Apple的产品
    results = collection.query(
        query_texts=["高端电子设备"],
        n_results=10,
        where={"brand": "Apple"}
    )
    print("品牌为Apple的产品:", results['documents'])
    
    # ============ 数值比较过滤 ============
    # 查询价格小于10000的产品（$lt小于, $lte小于等于, $gt大于, $gte大于等于）
    results = collection.query(
        query_texts=["电子设备"],
        n_results=10,
        where={"price": {"$lt": 10000}}
    )
    print("价格小于10000的产品:", results['documents'])
    
    # ============ 多条件组合 ============
    # 品牌为Apple且价格大于5000
    results = collection.query(
        query_texts=["电子设备"],
        n_results=10,
        where={
            "brand": "Apple",
            "price": {"$gte": 5000}
        }
    )
    print("Apple且价格>=5000:", results['documents'])
    
    # ============ $in 和 $nin 操作符 ============
    # 品牌在Apple或Samsung中
    results = collection.query(
        query_texts=["电子设备"],
        n_results=10,
        where={"brand": {"$in": ["Apple", "Samsung"]}}
    )
    print("Apple或Samsung品牌:", results['documents'])
    
    # ============ $exists 操作符 ============
    # 查询有in_stock字段的产品
    results = collection.query(
        query_texts=["电子设备"],
        n_results=10,
        where={"in_stock": {"$exists": True}}
    )
    print("有库存字段的产品:", results['documents'])
    
    # ============ 组合 $and 和 $or ============
    # 类别是手机或笔记本 且 价格小于15000
    results = collection.query(
        query_texts=["电子设备"],
        n_results=10,
        where={
            "$or": [
                {"category": "手机"},
                {"category": "笔记本"}
            ],
            "price": {"$lt": 15000}
        }
    )
    print("手机或笔记本且价格<15000:", results['documents'])


def document_content_filtering():
    """文档内容过滤"""
    
    import chromadb
    
    client = chromadb.PersistentClient(
        path="./content_filter_demo"
    )
    
    collection = client.get_or_create_collection(
        name="articles"
    )
    
    # 添加数据
    documents = [
        "Python深度学习入门指南",
        "JavaScript前端开发实战",
        "机器学习算法详解",
        "React现代Web开发",
        "神经网络原理"
    ]
    
    collection.add(
        documents=documents,
        ids=[f"doc{i}" for i in range(1, 6)],
        metadatas=[
            {"type": "技术", "level": "入门"},
            {"type": "前端", "level": "进阶"},
            {"type": "算法", "level": "高级"},
            {"type": "前端", "level": "入门"},
            {"type": "算法", "level": "高级"}
        ]
    )
    
    # 文档内容过滤 - 包含特定关键词
    results = collection.query(
        query_texts=["编程语言教程"],
        n_results=10,
        where_document={"$contains": "学习"}
    )
    print("包含'学习'的文档:", results['documents'])
    
    # $contains_any - 包含任意关键词
    results = collection.query(
        query_texts=["编程语言教程"],
        n_results=10,
        where_document={"$contains_any": ["Python", "JavaScript"]}
    )
    
    # $get 开始于
    results = collection.query(
        query_texts=["编程"],
        n_results=10,
        where_document={"$starts_with": "Python"}
    )
    print("以Python开头的文档:", results['documents'])


# 运行过滤示例
metadata_filtering()
