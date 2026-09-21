from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
from sklearn.svm import SVC
from sklearn.datasets import load_iris

iris = load_iris()
X, y = iris.data, iris.target

# One-vs-Rest
ovr_svm = OneVsRestClassifier(SVC(kernel='rbf', random_state=42))
ovr_svm.fit(X, y)
print(f"OvR准确率: {ovr_svm.score(X, y):.4f}")

# One-vs-One
ovo_svm = OneVsOneClassifier(SVC(kernel='rbf', random_state=42))
ovo_svm.fit(X, y)
print(f"OvO准确率: {ovo_svm.score(X, y):.4f}")

# sklearn直接支持
direct_svm = SVC(kernel='rbf', random_state=42)
direct_svm.fit(X, y)
print(f"直接多分类准确率: {direct_svm.score(X, y):.4f}")
