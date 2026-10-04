import numpy as np
import matplotlib.pyplot as plt

from sklearn.cluster import DBSCAN
from sklearn.datasets import make_moons

X_moons, y_moons = make_moons(n_samples=200, noise=0.1, random_state=42)

# K-Means（失败）
kmeans = KMeans(n_clusters=2, random_state=42, n_init=10)
y_kmeans = kmeans.fit_predict(X_moons)

# DBSCAN（成功）
dbscan = DBSCAN(eps=0.3, min_samples=5)
y_dbscan = dbscan.fit_predict(X_moons)

plt.figure(figsize=(12, 5))

plt.subplot(1, 3, 1)
plt.scatter(X_moons[:, 0], X_moons[:, 1], c=y_moons, cmap='viridis')
plt.title('真实标签')

plt.subplot(1, 3, 2)
plt.scatter(X_moons[:, 0], X_moons[:, 1], c=y_kmeans, cmap='viridis')
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], c='red', marker='X', s=200)
plt.title('K-Means（错误）')

plt.subplot(1, 3, 3)
plt.scatter(X_moons[:, 0], X_moons[:, 1], c=y_dbscan, cmap='viridis')
noise = X_moons[y_dbscan == -1]
if len(noise) > 0:
    plt.scatter(noise[:, 0], noise[:, 1], c='gray', marker='x', label='噪声')
    plt.legend()
plt.title('DBSCAN（正确）')

plt.tight_layout()
plt.savefig('dbscan_clustering.png', dpi=150)
plt.show()

print(f"DBSCAN发现簇数: {len(set(y_dbscan)) - (1 if -1 in y_dbscan else 0)}")
print(f"噪声点数量: {np.sum(y_dbscan == -1)}")

print("""
DBSCAN参数说明：
- eps: 邻域半径，控制点的邻域大小
- min_samples: 核心点所需的最小邻居数

优点：
- 不需要预设聚类数
- 可以发现任意形状的簇
- 可以识别噪声点
""")
