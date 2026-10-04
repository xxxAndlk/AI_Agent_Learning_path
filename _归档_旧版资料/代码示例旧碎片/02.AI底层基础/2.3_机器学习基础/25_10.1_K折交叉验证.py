from sklearn.model_selection import KFold, cross_val_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris

# 加载数据
iris = load_iris()
X, y = iris.data, iris.target

# 创建模型
rf = RandomForestClassifier(n_estimators=100, random_state=42)

# K折交叉验证 (5折)
kfold = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(rf, X, y, cv=kfold, scoring='accuracy')

print("=== 5折交叉验证结果 ===")
print(f"每折准确率: {scores}")
print(f"平均准确率: {scores.mean():.4f} (+/- {scores.std()*2:.4f})")
