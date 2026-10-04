from sklearn.svm import SVC
from sklearn.datasets import make_circles, make_moons

kernels = ['linear', 'poly', 'rbf', 'sigmoid']

data_circles, labels_circles = make_circles(n_samples=200, noise=0.1, factor=0.5, random_state=42)
data_moons, labels_moons = make_moons(n_samples=200, noise=0.1, random_state=42)

print("=== 不同核函数在两类数据上的准确率 ===\n")

for kernel in kernels:
    svc = SVC(kernel=kernel, random_state=42)
    svc.fit(data_circles, labels_circles)
    circle_acc = svc.score(data_circles, labels_circles)
    svc.fit(data_moons, labels_moons)
    moon_acc = svc.score(data_moons, labels_moons)
    print(f"{kernel:<10} 圆环数据: {circle_acc:.4f}  月亮数据: {moon_acc:.4f}")

print("""
核函数选择建议：
- 线性核：特征数多、样本数多，线性可分或接近线性可分
- RBF核：默认选择，通用性强，适合大多数情况
- 多项式核：特征交互重要，数据有一定结构性
- Sigmoid核：类似神经网络，适合特定场景
""")
