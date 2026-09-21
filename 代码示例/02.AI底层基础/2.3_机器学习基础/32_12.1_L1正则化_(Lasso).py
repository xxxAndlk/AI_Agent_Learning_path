from sklearn.linear_model import Lasso, LassoCV
from sklearn.preprocessing import StandardScaler
import numpy as np
import matplotlib.pyplot as plt

# 生成高维数据（特征数 > 样本数）
np.random.seed(42)
n_samples, n_features = 50, 200
X = np.random.randn(n_samples, n_features)
# 只有前10个特征真正有用
true_coef = np.zeros(n_features)
true_coef[:10] = np.random.randn(10) * 3
y = X @ true_coef + np.random.randn(n_samples) * 0.5

# 数据标准化（正则化对特征尺度敏感）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 使用交叉验证找最优alpha
alphas = np.logspace(-4, 1, 50)
lasso_cv = LassoCV(alphas=alphas, cv=5, random_state=42)
lasso_cv.fit(X_scaled, y)

print(f"最优alpha: {lasso_cv.alpha_:.4f}")
print(f"非零特征数: {np.sum(lasso_cv.coef_ != 0)}")
print(f"选中的特征索引: {np.where(lasso_cv.coef_ != 0)[0]}")
