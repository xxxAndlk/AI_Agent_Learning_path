import matplotlib.pyplot as plt
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.metrics import silhouette_score

# 层次聚类
agg = AgglomerativeClustering(n_clusters=4, linkage='ward')
y_agg = agg.fit_predict(X)

# 树状图
plt.figure(figsize=(12, 5))

plt.subplot(1, 2, 1)
linked = linkage(X, method='ward')
dendrogram(linked, truncate_mode='level', p=5)
plt.title('层次聚类树状图')

plt.subplot(1, 2, 2)
plt.scatter(X[:, 0], X[:, 1], c=y_agg, cmap='viridis')
plt.title('层次聚类结果')

plt.tight_layout()
plt.savefig('hierarchical_clustering.png', dpi=150)
plt.show()

# 不同链接方式对比
linkage_methods = ['ward', 'complete', 'average', 'single']
print("=== 不同链接方式 ===")
for method in linkage_methods:
    agg = AgglomerativeClustering(n_clusters=4, linkage=method)
    labels = agg.fit_predict(X)
    score = silhouette_score(X, labels)
    print(f"{method}: 轮廓系数={score:.4f}")
