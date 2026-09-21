# sklearn决策树不直接支持缺失值

# 解决方案1：预处理填充
from sklearn.impute import SimpleImputer
imputer = SimpleImputer(strategy='mean')
X_imputed = imputer.fit_transform(X)

# 解决方案2：使用支持缺失值的算法
# XGBoost, LightGBM等支持原生缺失值处理
