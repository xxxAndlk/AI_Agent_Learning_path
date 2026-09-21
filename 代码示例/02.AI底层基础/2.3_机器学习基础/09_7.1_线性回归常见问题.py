# 欠拟合：模型太简单，训练集误差大
# 解决方案：增加特征、使用更复杂模型、减少正则化

# 过拟合：模型太复杂，训练集误差小但测试集误差大
# 解决方案：正则化、减少特征、增加训练数据

# 正则化示例
from sklearn.linear_model import Ridge, Lasso

# L2正则化 (Ridge)
ridge = Ridge(alpha=1.0)  # alpha越大，正则化越强

# L1正则化 (Lasso) - 可以产生稀疏解
lasso = Lasso(alpha=0.1)  # 可用于特征选择
