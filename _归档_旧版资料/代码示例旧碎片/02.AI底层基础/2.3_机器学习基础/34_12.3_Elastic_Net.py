from sklearn.linear_model import ElasticNet, ElasticNetCV
import numpy as np

# 生成数据
np.random.seed(42)
X, y, coef = make_regression(
    n_samples=100, n_features=50,
    n_informative=15, coef=True, random_state=42
)

# 标准化
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 网格搜索最优参数
l1_ratios = [0.1, 0.3, 0.5, 0.7, 0.9, 0.95]
alphas = np.logspace(-4, 1, 20)

elastic_cv = ElasticNetCV(
    l1_ratio=l1_ratios,
    alphas=alphas,
    cv=5,
    max_iter=10000,
    random_state=42
)
elastic_cv.fit(X_scaled, y)

print(f"最优alpha: {elastic_cv.alpha_:.4f}")
print(f"最优L1比例: {elastic_cv.l1_ratio_:.2f}")
print(f"非零系数数: {np.sum(elastic_cv.coef_ != 0)}")
