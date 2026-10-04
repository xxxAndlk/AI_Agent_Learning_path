import numpy as np
import matplotlib.pyplot as plt

# 方法1: 累计解释方差
pca = PCA()
pca.fit(X_scaled)

cumulative_var = np.cumsum(pca.explained_variance_ratio_)
n_components_95 = np.argmax(cumulative_var >= 0.95) + 1
n_components_99 = np.argmax(cumulative_var >= 0.99) + 1

print(f"保留95%方差需要: {n_components_95} 个主成分")
print(f"保留99%方差需要: {n_components_99} 个主成分")

# 方法2: 碎石图
plt.figure(figsize=(8, 5))
plt.plot(range(1, 5), pca.explained_variance_, 'bo-')
plt.xlabel('主成分')
plt.ylabel('特征值')
plt.title('碎石图 - 找拐点')
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('scree_plot.png', dpi=150)
plt.show()
