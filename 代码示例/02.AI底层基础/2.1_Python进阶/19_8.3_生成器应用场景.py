def data_pipeline(raw_data):
    """深度学习数据预处理管道"""
    # 阶段1：数据清洗
    cleaned = (clean_sample(sample) for sample in raw_data)
    
    # 阶段2：数据过滤
    filtered = (sample for sample in cleaned if is_valid(sample))
    
    # 阶段3：数据增强
    augmented = (augment(sample) for sample in filtered)
    
    # 阶段4：批处理
    batch = []
    for sample in augmented:
        batch.append(sample)
        if len(batch) == 32:
            yield batch
            batch = []
    if batch:
        yield batch

# 使用：内存中只保留当前批次数据
for batch in data_pipeline(large_dataset):
    train_step(model, batch)
