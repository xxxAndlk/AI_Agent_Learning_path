from sklearn.model_selection import LeaveOneOut, cross_val_score
from sklearn.neighbors import KNeighborsClassifier

# 留一交叉验证（数据量大时非常慢）
# loocv = LeaveOneOut()
# 演示用小数据集
X_small = X[:50]  # 取前50个样本
y_small = y[:50]

loocv = LeaveOneOut()
model = KNeighborsClassifier(n_neighbors=3)
scores = cross_val_score(model, X_small, y_small, cv=loocv)

print(f"LOOCV准确率: {scores.mean():.4f}")
