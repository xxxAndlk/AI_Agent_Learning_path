# One-vs-Rest (OvR)：训练N个二分类器
# One-vs-One (OvO)：训练N(N-1)/2个二分类器

from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier

ovr = OneVsRestClassifier(LogisticRegression())
ovo = OneVsOneClassifier(LogisticRegression())
