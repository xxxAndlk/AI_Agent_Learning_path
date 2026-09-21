from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import load_iris
import numpy as np
import matplotlib.pyplot as plt

# 加载鸢尾花数据（4维）
iris = load_iris()
X_iris = iris.data
y_iris = iris.target

# 标准化（PCA对尺度敏感）
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X_iris)

# PCA降维到2维
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

print("=== PCA分析结果 ===")
print(f"原始维度: {X_iris.shape[1]}")
print(f"降维后维度: {X_pca.shape[1]}")
print(f"解释方差比例: {pca.explained_variance_ratio_}")
print(f"累计解释方差: {sum(pca.explained_variance_ratio_):.4f}")

# 可视化
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
for i in range(3):
    mask = y_iris == i
    plt.scatter(X_pca[mask, 0], X_pca[mask, 1], label=iris.target_names[i], alpha=0.7)
plt.xlabel('第一主成分')
plt.ylabel('第二主成分')
plt.title('PCA降维后的鸢尾花数据')
plt.legend()

# 累计解释方差
pca_full = PCA()
pca_full.fit(X_scaled)
cumulative_var = np.cumsum(pca_full.explained_variance_ratio_)

plt.subplot(1, 2, 2)
plt.plot(range(1, 5), pca_full.explained_variance_ratio_, 'ro-', label='单个主成分')
plt.plot(range(1, 5), cumulative_var, 'bo-', label='累计')
plt.xlabel('主成分数')
plt.ylabel('解释方差比例')
plt.title('主成分解释方差')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('pca_iris.png', dpi=150)
plt.show()
