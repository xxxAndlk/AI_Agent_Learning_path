# 问题：大量树导致预测速度慢

# 解决方案：
# 1. 减少树的数量（找到性能饱和点）
# 2. 并行训练
rf = RandomForestClassifier(n_estimators=100, n_jobs=-1)  # 使用所有CPU核心

# 3. 使用更高效的实现
from sklearn.ensemble import ExtraTreesClassifier  # Extremely Randomized Trees
# 比随机森林更快，随机选择分裂点
