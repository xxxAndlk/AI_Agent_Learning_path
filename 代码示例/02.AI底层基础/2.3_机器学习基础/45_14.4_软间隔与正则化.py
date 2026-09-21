import numpy as np
import matplotlib.pyplot as plt

# 软间隔SVM：C越小允许越多违规，C越大越严格
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

X_noisy = np.vstack([X, np.array([[0.5, 0.5], [-0.5, -0.5]])] * 20)
y_noisy = np.hstack([y, np.array([1, 0] * 20)])

for i, C in enumerate([0.01, 1, 100]):
    svc = SVC(kernel='rbf', C=C, gamma='scale')
    svc.fit(X_noisy, y_noisy)
    
    ax = axes[i]
    ax.scatter(X_noisy[y_noisy==0, 0], X_noisy[y_noisy==0, 1], c='blue', alpha=0.5)
    ax.scatter(X_noisy[y_noisy==1, 0], X_noisy[y_noisy==1, 1], c='red', alpha=0.5)
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()
    xx, yy = np.meshgrid(np.linspace(xlim[0], xlim[1], 200), np.linspace(ylim[0], ylim[1], 200))
    Z = svc.predict(np.c_[xx.ravel(), yy.ravel()])
    Z = Z.reshape(xx.shape)
    ax.contour(xx, yy, Z, colors='k', levels=[0.5], alpha=0.5)
    ax.set_title(f'C={C}, 准确率: {svc.score(X_noisy, y_noisy):.3f}')
    ax.axis('equal')

plt.tight_layout()
plt.savefig('svm_soft_margin.png', dpi=150)
plt.show()

print("""
C参数解释：
- C很小（如0.01）：更宽的间隔，允许更多误分类，泛化可能更好
- C很大（如100）：更窄的间隔，尽量正确分类所有样本，可能过拟合
""")
