def backward_pass_example(output, target, cache, weights):
    """手动实现反向传播"""
    m = target.shape[0]  # batch size
    
    # 输出层误差
    dz3 = output - target
    dw3 = cache['a2'].T @ dz3 / m
    db3 = dz3.sum(axis=0) / m
    
    # 传播到第二层（链式法则 + ReLU导数）
    da2 = dz3 @ weights['w3'].T
    dz2 = da2 * (cache['z2'] > 0)  # ReLU导数
    dw2 = cache['a1'].T @ dz2 / m
    db2 = dz2.sum(axis=0) / m
    
    # 传播到第一层
    da1 = dz2 @ weights['w2'].T
    dz1 = da1 * (cache['z1'] > 0)
    dw1 = ...  # 类似计算
    
    return {'dw1': dw1, 'db1': db1, 'dw2': dw2, 'db2': db2, 'dw3': dw3, 'db3': db3}
