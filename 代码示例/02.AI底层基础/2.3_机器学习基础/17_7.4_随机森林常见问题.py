# 问题：存储大量树消耗内存

# 解决方案：
# 1. 限制树的深度
# 2. 使用warm_start逐步增加树
rf = RandomForestClassifier(warm_start=True)
for n_trees in [50, 100, 150]:
    rf.n_estimators = n_trees
    rf.fit(X, y)
    # 评估性能，决定是否继续
