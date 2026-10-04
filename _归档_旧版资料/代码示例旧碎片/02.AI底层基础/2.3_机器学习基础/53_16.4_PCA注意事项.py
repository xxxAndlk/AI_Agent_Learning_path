print("""
PCA使用注意事项：

1. 数据标准化
   - PCA对特征尺度敏感，使用前必须标准化
   - 使用StandardScaler

2. 解释方差
   - 不要只看前几个主成分
   - 根据累计解释方差选择合适的维度

3. 线性假设
   - PCA假设数据的主要变化是线性的
   - 对于非线性数据，考虑使用t-SNE或UMAP

4. 降维目的
   - 可视化：降到2-3维
   - 加速其他算法：保留95%以上方差
   - 去除噪声：选择能解释大部分方差的主成分
""")

# 查看主成分的组成
pca_iris = PCA(n_components=2)
pca_iris.fit(StandardScaler().fit_transform(iris.data))

print("\n主成分1的各特征权重:")
for name, weight in zip(iris.feature_names, pca_iris.components_[0]):
    print(f"  {name}: {weight:.4f}")
