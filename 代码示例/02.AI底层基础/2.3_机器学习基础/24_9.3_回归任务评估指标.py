import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score

# 真实值和预测值
y_true = np.array([3.0, 4.5, 5.0, 2.0, 8.0])
y_pred = np.array([2.8, 4.2, 5.5, 2.2, 7.5])

# 均方误差 (MSE) - 对大误差惩罚更重
mse = mean_squared_error(y_true, y_pred)
print(f"MSE: {mse:.4f}")

# 均方根误差 (RMSE) - 与目标值同一尺度
rmse = np.sqrt(mse)
print(f"RMSE: {rmse:.4f}")

# 平均绝对误差 (MAE) - 对异常值更鲁棒
mae = mean_absolute_error(y_true, y_pred)
print(f"MAE: {mae:.4f}")

# R²分数 - 衡量模型解释方差的比例
r2 = r2_score(y_true, y_pred)
print(f"R²: {r2:.4f}")
# R²=1 表示完美预测
# R²=0 表示用均值预测
# R²<0 表示比均值预测还差
