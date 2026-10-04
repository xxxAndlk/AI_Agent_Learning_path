import numpy as np
# 批量梯度下降示例
def batch_gradient_descent(X, y, lr=0.01, n_iters=1000):
    """批量梯度下降 - 每次使用全部样本"""
    m, n = X.shape
    w = np.zeros(n)
    b = 0
    
    for _ in range(n_iters):
        y_pred = X @ w + b
        dw = (1/m) * X.T @ (y_pred - y)
        db = (1/m) * np.sum(y_pred - y)
        w -= lr * dw
        b -= lr * db
    
    return w, b
