def fine_tune_for_medical_domain():
    """医学领域Embedding微调示例"""
    
    # 初始化微调器
    tuner = EmbeddingFineTuner(
        base_model='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
    )
    
    # 添加训练数据（医学问答对）
    medical_pairs = [
        # 相似对（正样本）
        ("高血压的诊断标准是什么？", "如何判断是否患有高血压？", 1),
        ("糖尿病患者应该吃什么食物？", "糖尿病人的饮食建议", 1),
        ("冠心病的症状有哪些？", "心脏病发作的预兆", 1),
        # 不相似对（负样本）
        ("如何治疗感冒？", "骨折的康复方法", 0),
        ("维生素C的作用", "糖尿病的并发症", 0),
    ]
    
    pairs, labels = zip(*medical_pairs)
    tuner.add_training_data(pairs, labels)
    
    # 微调
    tuner.fine_tune(
        num_epochs=5,
        batch_size=8,
        learning_rate=1e-5
    )
    
    # 保存
    tuner.save_model('./medical-embedding')
    
    print("医学领域Embedding模型微调完成")


def fine_tune_with_triplets():
    """使用三元组数据进行微调"""
    
    tuner = EmbeddingFineTuner(
        base_model='sentence-transformers/all-MiniLM-L6-v2'
    )
    
    # 添加三元组数据
    triplets = [
        ("如何预防心脏病", "运动和健康饮食可以预防心脏病", "今天天气怎么样"),
        ("Python是什么", "Python是一种编程语言", "水果沙拉的做法"),
        ("机器学习的应用", "机器学习用于图像识别和自然语言处理", "历史事件的日期"),
    ]
    
    for anchor, positive, negative in triplets:
        tuner.add_triplet_data(anchor, positive, negative)
    
    # 微调（三元组损失）
    tuner.fine_tune(
        num_epochs=3,
        loss_type='triplet'
    )
    
    print("三元组微调完成")
