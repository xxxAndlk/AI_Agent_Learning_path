# 问题：特征尺度差异大导致收敛慢
# 示例：特征1范围[0,1]，特征2范围[0,10000]

# 解决方案：标准化或归一化
from sklearn.preprocessing import StandardScaler, MinMaxScaler

# 标准化 (均值为0，标准差为1)
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# 归一化 (缩放到[0,1])
minmax = MinMaxScaler()
X_normalized = minmax.fit_transform(X)
