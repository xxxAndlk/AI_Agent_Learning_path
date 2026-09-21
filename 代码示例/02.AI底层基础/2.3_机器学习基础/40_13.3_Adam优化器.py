import numpy as np
def adam_optimizer(X, y, lr=0.001, n_iters=1000, 
                   beta1=0.9, beta2=0.999, epsilon=1e-8):
    """Adam优化器"""
    m, n = X.shape
    w = np.zeros(n)
    b = 0
    
    m_w = np.zeros(n)
    v_w = np.zeros(n)
    m_b = 0
    v_b = 0
    
    for t in range(1, n_iters + 1):
        y_pred = X @ w + b
        dw = (1/m) * X.T @ (y_pred - y)
        db = (1/m) * np.sum(y_pred - y)
        
        m_w = beta1 * m_w + (1 - beta1) * dw
        m_b = beta1 * m_b + (1 - beta1) * db
        
        v_w = beta2 * v_w + (1 - beta2) * (dw ** 2)
        v_b = beta2 * v_b + (1 - beta2) * (db ** 2)
        
        m_w_hat = m_w / (1 - beta1 ** t)
        m_b_hat = m_b / (1 - beta1 ** t)
        v_w_hat = v_w / (1 - beta2 ** t)
        v_b_hat = v_b / (1 - beta2 ** t)
        
        w -= lr * m_w_hat / (np.sqrt(v_w_hat) + epsilon)
        b -= lr * m_b_hat / (np.sqrt(v_b_hat) + epsilon)
    
    return w, b
