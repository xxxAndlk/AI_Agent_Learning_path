import numpy as np
def gradient_descent_with_momentum(X, y, lr=0.01, momentum=0.9, n_iters=1000):
    """带动量的梯度下降"""
    m, n = X.shape
    w = np.zeros(n)
    b = 0
    
    v_w = np.zeros(n)
    v_b = 0
    
    for _ in range(n_iters):
        y_pred = X @ w + b
        dw = (1/m) * X.T @ (y_pred - y)
        db = (1/m) * np.sum(y_pred - y)
        
        v_w = momentum * v_w - lr * dw
        v_b = momentum * v_b - lr * db
        
        w += v_w
        b += v_b
    
    return w, b
