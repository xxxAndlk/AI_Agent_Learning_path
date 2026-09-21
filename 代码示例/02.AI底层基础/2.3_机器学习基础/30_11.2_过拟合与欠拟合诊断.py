import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error

# 生成非线性数据
np.random.seed(42)
X = np.sort(np.random.rand(50, 1) * 6 - 3, axis=1)
y = np.sin(X).ravel() + np.random.randn(50) * 0.3  # 添加噪声

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# 不同复杂度的模型
degrees = [1, 3, 10, 15]
train_errors = []
test_errors = []

plt.figure(figsize=(12, 8))

for i, degree in enumerate(degrees):
    # 创建多项式回归模型
    model = Pipeline([
        ('poly', PolynomialFeatures(degree=degree)),
        ('linear', LinearRegression())
    ])
    
    model.fit(X_train, y_train)
    
    # 计算训练和测试误差
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    
    train_mse = mean_squared_error(y_train, train_pred)
    test_mse = mean_squared_error(y_test, test_pred)
    
    train_errors.append(train_mse)
    test_errors.append(test_mse)
    
    # 可视化拟合效果
    plt.subplot(2, 2, i + 1)
    X_plot = np.linspace(-3, 3, 100).reshape(-1, 1)
    y_plot = model.predict(X_plot)
    
    plt.scatter(X_train, y_train, c='blue', alpha=0.5, label='训练数据')
    plt.scatter(X_test, y_test, c='red', alpha=0.5, label='测试数据')
    plt.plot(X_plot, y_plot, 'g-', linewidth=2)
    plt.plot(X_plot, np.sin(X_plot), 'k--', alpha=0.5, label='真实函数')
    plt.title(f'多项式阶数={degree}\n训练MSE={train_mse:.3f}, 测试MSE={test_mse:.3f}')
    plt.legend()
    plt.ylim(-2, 2)

plt.tight_layout()
plt.savefig('bias_variance_demo.png', dpi=150)
plt.show()

# 打印误差对比
print("=== 不同复杂度模型的误差对比 ===")
print(f"{'degree':<10} {'训练MSE':<15} {'测试MSE':<15}")
print("-" * 40)
for d, train_e, test_e in zip(degrees, train_errors, test_errors):
    print(f"{d:<10} {train_e:<15.4f} {test_e:<15.4f}")
