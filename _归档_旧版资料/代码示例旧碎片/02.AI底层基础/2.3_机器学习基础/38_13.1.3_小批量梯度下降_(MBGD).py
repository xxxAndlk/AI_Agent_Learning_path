import numpy as np
def mini_batch_gradient_descent(X, y, lr=0.01, batch_size=32, n_iters=1000):
    """小批量梯度下降 - 每次使用batch_size个样本"""
    m, n = X.shape
    w = np.zeros(n)
    b = 0
    
    for _ in range(n_iters):
        indices = np.random.permutation(m)
        X_shuffled = X[indices]
        y_shuffled = y[indices]
        
        for start in range(0, m, batch_size):
            end = min(start + batch_size, m)
            X_batch = X_shuffled[start:end]
            y_batch = y_shuffled[start:end]
            
            y_pred = X_batch @ w + b
            dw = (1/len(y_batch)) * X_batch.T @ (y_pred - y_batch)
            db = (1/len(y_batch)) * np.sum(y_pred - y_batch)
            
            w -= lr * dw
            b -= lr * db
    
    return w, b
