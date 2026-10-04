from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.metrics import silhouette_score
import numpy as np
import matplotlib.pyplot as plt

# 生成模拟数据
X, y_true = make_blobs(n_samples=300, centers=4, cluster_std=0.8, random_state=42)

# K-Means聚类
kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
y_pred = kmeans.fit_predict(X)

# 可视化
plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.scatter(X[:, 0], X[:, 1], c=y_true, cmap='viridis', alpha=0.7)
plt.title('真实标签')

plt.subplot(1, 3, 2)
plt.scatter(X[:, 0], X[:, 1], c=y_pred, cmap='viridis', alpha=0.7)
plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[:, 1], 
            c='red', marker='X', s=200, label='聚类中心')
plt.title('K-Means预测')
plt.legend()

# 肘部法则确定K值
plt.subplot(1, 3, 3)
inertias = []
K_range = range(1, 11)
for k in K_range:
    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    km.fit(X)
    inertias.append(km.inertia_)

plt.plot(K_range, inertias, 'bo-')
plt.xlabel('聚类数 K')
plt.ylabel('惯性 (Inertia)')
plt.title('肘部法则')
plt.xticks(K_range)

plt.tight_layout()
plt.savefig('kmeans_clustering.png', dpi=150)
plt.show()

print(f"轮廓系数: {silhouette_score(X, y_pred):.4f}")
