def forward_pass_example(x, weights, biases):
    """手动实现前向传播"""
    # 第一层
    z1 = x @ weights['w1'] + biases['b1']  # 线性变换
    a1 = relu(z1)                          # 非线性激活
    
    # 第二层
    z2 = a1 @ weights['w2'] + biases['b2']
    a2 = relu(z2)
    
    # 输出层
    z3 = a2 @ weights['w3'] + biases['b3']
    output = z3  # 回归任务通常不加激活
    
    return output, {'z1': z1, 'a1': a1, 'z2': z2, 'a2': a2}
