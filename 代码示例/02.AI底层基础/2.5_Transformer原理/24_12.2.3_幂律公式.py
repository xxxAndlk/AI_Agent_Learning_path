# 预测模型性能
def predict_loss(compute_flops, params, tokens):
    """
    基于缩放定律预测loss
    """
    # 经验系数（来自OpenAI论文）
    alpha_N = 0.276  # 参数缩放指数
    alpha_D = 0.095  # 数据缩放指数
    alpha_C = 0.050  # 计算量缩放指数
    
    # 常数项（需校准）
    L0 = 1.99  # 无穷模型的理论最小loss
    c_N = 406.4
    c_D = 410.7
    
    L_N = (params / c_N) ** (-alpha_N)
    L_D = (tokens / c_D) ** (-alpha_D)
    
    # 组合
    L = L0 + L_N + L_D
    
    return L
