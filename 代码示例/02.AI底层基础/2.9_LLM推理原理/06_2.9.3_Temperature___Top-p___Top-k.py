"""
Temperature、Top-p、Top-k采样策略实现
展示这些参数如何影响生成结果
"""

import torch                        # PyTorch框架
import torch.nn.functional as F     # 激活函数
from typing import Tuple, Optional  # 类型提示

class AdvancedSampling:
    """高级采样策略实现"""
    
    @staticmethod
    def apply_temperature(logits: torch.Tensor, temperature: float) -> torch.Tensor:
        """
        应用温度参数
        
        原理：
        - temperature缩放logits: logits / temperature
        - 高温度使分布更平坦（更随机）
        - 低温度使分布更尖锐（更确定）
        
        参数:
            logits: 原始logits
            temperature: 温度值，必须>0
        返回:
            缩放后的logits
        """
        if temperature <= 0:
            raise ValueError("温度必须大于0")
        
        return logits / temperature
    
    @staticmethod
    def top_p_sampling(
        logits: torch.Tensor,
        p: float = 0.9,
        temperature: float = 1.0
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        Top-p（核采样）实现
        
        原理：
        1. 按概率降序排列所有token
        2. 计算累积概率
        3. 保留累积概率<=p的最小token集合
        4. 在这个集合中重新归一化并采样
        
        参数:
            logits: 模型输出logits
            p: 累积概率阈值（0-1）
            temperature: 温度参数
        返回:
            (采样的token ID, 过滤后的概率分布)
        """
        # 应用温度
        scaled_logits = logits / temperature
        
        # 转为概率
        probs = F.softmax(scaled_logits, dim=-1)
        
        # 按概率降序排序
        sorted_probs, sorted_indices = torch.sort(probs, descending=True, dim=-1)
        
        # 计算累积概率
        cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
        
        # 创建掩码：保留累积概率<=p的token
        # 注意：至少保留第一个（概率最高的）
        sorted_indices_to_remove = cumulative_probs > p
        # 右移一位，确保至少保留第一个
        sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
        sorted_indices_to_remove[..., 0] = False
        
        # 将要移除的token概率设为0
        sorted_probs[sorted_indices_to_remove] = 0.0
        
        # 重新归一化
        sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True)
        
        # 从过滤后的分布中采样
        sampled_index = torch.multinomial(sorted_probs, num_samples=1)
        
        # 映射回原始索引
        next_token = sorted_indices.gather(dim=-1, index=sampled_index)
        
        return next_token, sorted_probs
    
    @staticmethod
    def top_k_top_p_sampling(
        logits: torch.Tensor,
        top_k: int = 50,
        top_p: float = 0.95,
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        组合Top-k和Top-p采样
        
        这是最常用的采样配置：
        1. 先应用Top-k截断
        2. 再应用Top-p截断
        3. 应用温度
        4. 采样
        
        参数:
            logits: 模型输出logits
            top_k: Top-k参数
            top_p: Top-p参数
            temperature: 温度参数
        返回:
            采样的token ID
        """
        # Step 1: Top-k过滤
        if top_k > 0:
            # 获取第k大的值作为阈值
            top_k = min(top_k, logits.size(-1))  # 确保k不超过词汇表大小
            values, _ = torch.topk(logits, top_k, dim=-1)
            min_value = values[..., -1, None]  # 第k大的值
            # 将非top-k的位置设为负无穷
            logits = torch.where(
                logits < min_value,
                torch.tensor(float('-inf'), device=logits.device),
                logits
            )
        
        # Step 2: Top-p过滤
        if top_p < 1.0:
            # 转为概率
            probs = F.softmax(logits / temperature, dim=-1)
            
            # 排序并计算累积概率
            sorted_probs, sorted_indices = torch.sort(probs, descending=True)
            cumulative_probs = torch.cumsum(sorted_probs, dim=-1)
            
            # 创建移除掩码
            sorted_indices_to_remove = cumulative_probs > top_p
            sorted_indices_to_remove[..., 1:] = sorted_indices_to_remove[..., :-1].clone()
            sorted_indices_to_remove[..., 0] = False
            
            # 将移除位置的概率设为0
            sorted_probs[sorted_indices_to_remove] = 0.0
            
            # 重新归一化
            sorted_probs = sorted_probs / sorted_probs.sum(dim=-1, keepdim=True)
            
            # 采样并映射
            sampled_index = torch.multinomial(sorted_probs, num_samples=1)
            next_token = sorted_indices.gather(dim=-1, index=sampled_index)
            
            return next_token
        
        # 如果只有Top-k，直接采样
        probs = F.softmax(logits / temperature, dim=-1)
        next_token = torch.multinomial(probs, num_samples=1)
        
        return next_token


def visualize_temperature_effect():
    """可视化温度对概率分布的影响"""
    
    print("=" * 60)
    print("温度参数对概率分布的影响")
    print("=" * 60)
    
    # 模拟logits（假设有5个token）
    logits = torch.tensor([[2.0, 1.5, 0.5, 0.3, 0.1]])
    
    temperatures = [0.5, 1.0, 1.5, 2.0]
    
    print(f"\n原始logits: {logits[0].tolist()}")
    print("\n不同温度下的概率分布:\n")
    
    for temp in temperatures:
        scaled_logits = logits / temp
        probs = F.softmax(scaled_logits, dim=-1)
        print(f"温度={temp}: {[f'{p:.4f}' for p in probs[0].tolist()]}")


def demonstrate_top_p():
    """演示Top-p采样"""
    
    print("\n" + "=" * 60)
    print("Top-p采样演示")
    print("=" * 60)
    
    # 创建一个有明确峰值的分布
    logits = torch.tensor([[3.0, 2.5, 1.0, 0.5, 0.3, 0.2, 0.1, 0.05, 0.02, 0.01]])
    
    probs = F.softmax(logits, dim=-1)
    print(f"\n原始概率分布: {[f'{p:.4f}' for p in probs[0].tolist()]}")
    
    # 计算累积概率
    sorted_probs, sorted_indices = torch.sort(probs, descending=True)
    cumulative = torch.cumsum(sorted_probs, dim=-1)
    print(f"\n排序后累积概率: {[f'{c:.4f}' for c in cumulative[0].tolist()]}")
    
    # 不同p值的效果
    p_values = [0.5, 0.8, 0.95]
    
    for p in p_values:
        token, filtered_probs = AdvancedSampling.top_p_sampling(logits, p=p)
        print(f"\np={p}: 选中token {token.item()}")
        print(f"  保留的token数量: {(filtered_probs > 0).sum().item()}")


def compare_all_strategies():
    """综合对比所有采样策略"""
    
    print("\n" + "=" * 60)
    print("采样策略综合对比")
    print("=" * 60)
    
    # 模拟一个实际的logits分布
    torch.manual_seed(42)
    logits = torch.randn(1, 100)  # 假设词汇表大小100
    
    configs = [
        {"name": "贪婪", "temp": 0, "top_k": 0, "top_p": 1.0},
        {"name": "低温采样", "temp": 0.3, "top_k": 0, "top_p": 1.0},
        {"name": "标准采样", "temp": 1.0, "top_k": 0, "top_p": 1.0},
        {"name": "Top-K(50)", "temp": 1.0, "top_k": 50, "top_p": 1.0},
        {"name": "Top-P(0.9)", "temp": 1.0, "top_k": 0, "top_p": 0.9},
        {"name": "Top-K+Top-P", "temp": 0.8, "top_k": 50, "top_p": 0.95},
    ]
    
    print("\n不同配置下的采样结果（各采样5次）:\n")
    
    for config in configs:
        results = []
        for _ in range(5):
            if config["temp"] == 0:  # 贪婪采样
                result = torch.argmax(logits, dim=-1).item()
            else:
                result = AdvancedSampling.top_k_top_p_sampling(
                    logits,
                    top_k=config["top_k"],
                    top_p=config["top_p"],
                    temperature=config["temp"]
                ).item()
            results.append(result)
        
        print(f"{config['name']:15s}: {results}")


if __name__ == "__main__":
    visualize_temperature_effect()
    demonstrate_top_p()
    compare_all_strategies()
