import math

def calculate_window_size(model_context_limit: int, avg_tokens_per_message: int = 30) -> int:
    """
    根据模型上下文限制计算合适的窗口大小
    
    Args:
        model_context_limit: 模型最大上下文Token数
        avg_tokens_per_message: 每条消息平均Token数
    """
    # 预留空间给系统提示和当前输入
    available_tokens = model_context_limit * 0.6
    # 每轮对话有用户消息和AI回复
    tokens_per_turn = avg_tokens_per_message * 2
    return math.floor(available_tokens / tokens_per_turn)

# GPT-5.4 上下文限制128K
optimal_k = calculate_window_size(128000)
print(f"GPT-5.4推荐窗口大小: k={optimal_k}")
