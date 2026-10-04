import numpy as np
def stochastic_gradient_descent(X, y, lr=0.01, n_iters=1000):
    """随机梯度下降 - 每次使用一个样本"""
    m, n = X.shape
    w = np.zeros(n)
    b = 0
    
    for _ in range(n_iters):
        indices = np.random.permutation(m)
        X_shuffled = X[indices]
        y_shuffled = y[indices]
        
        for i in range(m):
            xi = X_shuffled[i:i+1]
            yi = y_shuffled[i]
            y_pred = xi @ w + b
            dw = xi.T * (y_pred - yi)
            db = y_pred - yi
            w -= lr * dw.ravel()
            b -= lr * db
    
    return w, b
