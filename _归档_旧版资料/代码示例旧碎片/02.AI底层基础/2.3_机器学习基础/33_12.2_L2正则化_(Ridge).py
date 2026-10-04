from sklearn.linear_model import Ridge, RidgeCV
from sklearn.datasets import make_regression
import numpy as np

# 生成有多重共线性的数据
X, y, coef = make_regression(
    n_samples=100, 
    n_features=50,
    n_informative=10,
    coef=True,
    random_state=42
)

# 添加高度相关的特征（共线性）
X = np.hstack([X, X[:, :10] + np.random.randn(100, 10) * 0.1])

# 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 交叉验证找最优alpha
alphas = np.logspace(-3, 5, 100)
ridge_cv = RidgeCV(alphas=alphas, cv=5)
ridge_cv.fit(X_scaled, y)

print(f"最优alpha: {ridge_cv.alpha_:.4f}")
