# 问题：线性逻辑回归只能学习线性边界

# 解决方案：多项式特征
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import Pipeline

model = Pipeline([
    ('poly', PolynomialFeatures(degree=2)),  # 添加多项式特征
    ('logistic', LogisticRegression())
])
