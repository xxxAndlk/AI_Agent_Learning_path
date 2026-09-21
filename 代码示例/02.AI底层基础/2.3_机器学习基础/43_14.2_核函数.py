from sklearn.svm import SVC
import numpy as np
import matplotlib.pyplot as plt

# 生成非线性可分数据
np.random.seed(42)
theta = np.random.uniform(0, 2*np.pi, 100)
r = np.random.uniform(0, 1, 100)
X1 = np.column_stack([r * np.cos(theta), r * np.sin(theta)])
y1 = np.zeros(100)

theta2 = np.random.uniform(0, 2*np.pi, 100)
r2 = np.random.uniform(2, 3, 100)
X2 = np.column_stack([r2 * np.cos(theta2), r2 * np.sin(theta2)])
y2 = np.ones(100)

X = np.vstack([X1, X2])
y = np.hstack([y1, y2])

# 可视化原始数据
plt.figure(figsize=(15, 5))

plt.subplot(1, 3, 1)
plt.scatter(X1[:, 0], X1[:, 1], c='blue', label='类别0')
plt.scatter(X2[:, 0], X2[:, 1], c='red', label='类别1')
plt.title('原始数据（同心圆）')
plt.legend()
plt.axis('equal')

# 线性SVM（无法分开）
svm_linear = SVC(kernel='linear', C=1.0)
svm_linear.fit(X, y)

plt.subplot(1, 3, 2)
plt.scatter(X1[:, 0], X1[:, 1], c='blue', alpha=0.5)
plt.scatter(X2[:, 0], X2[:, 1], c='red', alpha=0.5)
ax = plt.gca()
xlim = ax.get_xlim()
ylim = ax.get_ylim()
xx, yy = np.meshgrid(np.linspace(xlim[0], xlim[1], 200), np.linspace(ylim[0], ylim[1], 200))
Z = svm_linear.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contour(xx, yy, Z, colors='k', levels=[0.5], alpha=0.5)
plt.title(f'线性核准确率: {svm_linear.score(X, y):.2f}')

# RBF核SVM
svm_rbf = SVC(kernel='rbf', C=1.0, gamma='scale')
svm_rbf.fit(X, y)

plt.subplot(1, 3, 3)
plt.scatter(X1[:, 0], X1[:, 1], c='blue', alpha=0.5)
plt.scatter(X2[:, 0], X2[:, 1], c='red', alpha=0.5)
Z = svm_rbf.predict(np.c_[xx.ravel(), yy.ravel()])
Z = Z.reshape(xx.shape)
plt.contour(xx, yy, Z, colors='k', levels=[0.5], alpha=0.5)
plt.title(f'RBF核准确率: {svm_rbf.score(X, y):.2f}')

plt.tight_layout()
plt.savefig('svm_kernels.png', dpi=150)
plt.show()

print(f"线性核准确率: {svm_linear.score(X, y):.4f}")
print(f"RBF核准确率: {svm_rbf.score(X, y):.4f}")
