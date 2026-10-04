"""
采样策略对比示例
展示Greedy、Random Sampling等不同策略的效果
"""

import torch                        # PyTorch框架
import torch.nn.functional as F     # 激活函数
from typing import List, Tuple      # 类型提示

class SamplingStrategies:
    """各种采样策略的实现"""
    
    @staticmethod
    def greedy_sampling(logits: torch.Tensor) -> torch.Tensor:
        """
        贪婪采样：选择概率最高的token
        
        特点：
        - 确定性：相同输入总是产生相同输出
        - 缺点：容易陷入重复，缺乏多样性
        
        参数:
            logits: 模型输出的logits，shape: (batch, vocab_size)
        返回:
            选中的token ID
        """
        # argmax返回最大值的索引
        next_token = torch.argmax(logits, dim=-1, keepdim=True)
        return next_token
    
    @staticmethod
    def random_sampling(logits: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        """
        随机采样：按概率分布随机选择token
        
        特点：
        - 引入随机性，生成更多样化
        - temperature控制随机程度
        
        参数:
            logits: 模型输出的logits
            temperature: 温度参数
        返回:
            采样的token ID
        """
        # 温度缩放
        scaled_logits = logits / temperature
        
        # 转为概率分布
        probs = F.softmax(scaled_logits, dim=-1)
        
        # 按概率采样
        next_token = torch.multinomial(probs, num_samples=1)
        
        return next_token
    
    @staticmethod
    def top_k_sampling(
        logits: torch.Tensor, 
        k: int = 50,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        Top-K采样：只从概率最高的K个token中采样
        
        特点：
        - 截断低概率token，避免生成无意义内容
        - 保留一定多样性
        
        参数:
            logits: 模型输出的logits
            k: 保留的token数量
            temperature: 温度参数
        返回:
            采样的token ID
        """
        # 获取top-k的值和索引
        top_k_values, top_k_indices = torch.topk(logits, k, dim=-1)
        
        # 将非top-k的位置设为负无穷（softmax后概率为0）
        # 创建一个全为负无穷的tensor
        filtered_logits = torch.full_like(logits, float('-inf'))
        
        # 将top-k位置的值填入
        filtered_logits.scatter_(dim=-1, index=top_k_indices, src=top_k_values)
        
        # 应用温度
        scaled_logits = filtered_logits / temperature
        
        # 转为概率并采样
        probs = F.softmax(scaled_logits, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        
        return next_token


def compare_sampling_strategies():
    """对比不同采样策略的效果"""
    
    print("=" * 60)
    print("采样策略对比演示")
    print("=" * 60)
    
    # 模拟logits（假设词汇表大小为10，便于演示）
    # 假设模型认为token 3 和 token 7 概率较高
    logits = torch.tensor([[1.0, 0.5, 0.3, 5.0, 0.2, 0.1, 0.8, 4.5, 0.4, 0.6]])
    
    print(f"\n输入logits: {logits[0].tolist()}")
    
    # 计算概率分布
    probs = F.softmax(logits, dim=-1)
    print(f"对应概率: {[f'{p:.3f}' for p in probs[0].tolist()]}")
    print(f"概率最高的是token {torch.argmax(logits).item()}")
    
    # 1. 贪婪采样
    print("\n--- 1. 贪婪采样 (Greedy) ---")
    greedy_result = SamplingStrategies.greedy_sampling(logits)
    print(f"结果: token {greedy_result.item()}")
    print("特点: 总是选择概率最高的，输出确定")
    
    # 2. 随机采样（不同温度）
    print("\n--- 2. 随机采样 (Random) ---")
    
    # 低温度（更确定）
    torch.manual_seed(42)
    low_temp_result = SamplingStrategies.random_sampling(logits, temperature=0.5)
    print(f"低温度(0.5): token {low_temp_result.item()} - 倾向选择高概率token")
    
    # 高温度（更随机）
    torch.manual_seed(42)
    high_temp_result = SamplingStrategies.random_sampling(logits, temperature=2.0)
    print(f"高温度(2.0): token {high_temp_result.item()} - 更均匀分布，可能选低概率token")
    
    # 3. Top-K采样
    print("\n--- 3. Top-K采样 ---")
    torch.manual_seed(42)
    top_k_result = SamplingStrategies.top_k_sampling(logits, k=3, temperature=1.0)
    print(f"K=3: token {top_k_result.item()} - 只从前3个高概率token中采样")
    
    # 多次采样展示多样性
    print("\n--- 多次采样展示多样性 ---")
    print("贪婪采样5次:", [SamplingStrategies.greedy_sampling(logits).item() for _ in range(5)])
    
    torch.manual_seed(42)
    print("随机采样5次:", [SamplingStrategies.random_sampling(logits, 0.8).item() for _ in range(5)])


if __name__ == "__main__":
    compare_sampling_strategies()
