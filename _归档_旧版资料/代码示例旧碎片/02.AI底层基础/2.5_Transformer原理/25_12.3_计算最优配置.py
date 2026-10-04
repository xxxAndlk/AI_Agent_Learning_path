import numpy as np

def compute_optimal_allocation(
    compute_budget_flops: float,
    price_per_flops: float = 0.0
):
    """
    计算计算量最优的模型配置
    
    基于Chinchilla论文的发现
    """
    # Chinchilla最优配置经验公式
    # 数据量应该是参数量的约20倍
    
    # 参数量（假设使用约50%计算量训练模型）
    optimal_params = (compute_budget_flops / 6e9) ** 0.5
    
    # 数据量（约为参数量的20倍）
    optimal_tokens = optimal_params * 20
    
    return {
        'optimal_params': optimal_params,
        'optimal_tokens': optimal_tokens,
        'training_steps': optimal_tokens / optimal_params
    }

# 示例计算
config = compute_optimal_allocation(compute_budget_flops=1e21)  # 约10^21 FLOPs
print(f"最优参数量: {config['optimal_params']/1e9:.1f}B")
print(f"最优训练token数: {config['optimal_tokens']/1e12:.1f}T")
