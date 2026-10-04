"""
Beam Search实现
展示如何通过保留多个候选序列获得更好的生成结果
"""

import torch                        # PyTorch框架
import torch.nn.functional as F     # 神经网络函数
from typing import List, Tuple      # 类型提示
from dataclasses import dataclass   # 数据类装饰器

@dataclass
class BeamCandidate:
    """Beam Search候选序列"""
    tokens: List[int]               # token序列
    score: float                    # 累积得分（对数概率和）
    
    def __lt__(self, other):
        """定义比较运算符，用于排序"""
        return self.score < other.score


class BeamSearch:
    """Beam Search实现"""
    
    def __init__(
        self,
        beam_size: int = 5,
        max_length: int = 50,
        length_penalty: float = 1.0,
        eos_token_id: int = 1
    ):
        """
        初始化Beam Search
        
        参数:
            beam_size: beam大小（保留的候选数量）
            max_length: 最大生成长度
            length_penalty: 长度惩罚系数
                - 1.0: 无惩罚
                - >1.0: 偏好更长的序列
                - <1.0: 偏好更短的序列
            eos_token_id: 结束符token ID
        """
        self.beam_size = beam_size
        self.max_length = max_length
        self.length_penalty = length_penalty
        self.eos_token_id = eos_token_id
    
    def _length_normalize(self, score: float, length: int) -> float:
        """
        长度归一化
        
        避免Beam Search偏好短序列的问题
        
        参数:
            score: 原始得分
            length: 序列长度
        返回:
            归一化后的得分
        """
        # 常用的长度归一化公式
        return score / (length ** self.length_penalty)
    
    def search(
        self,
        model_forward,               # 模型的前向传播函数
        input_ids: torch.Tensor,     # 输入序列
    ) -> List[Tuple[List[int], float]]:
        """
        执行Beam Search
        
        参数:
            model_forward: 模型前向函数，输入token序列，返回logits
            input_ids: 初始输入序列
        返回:
            List of (token序列, 得分) 元组，按得分降序排列
        """
        batch_size = input_ids.shape[0]
        
        # 初始化beam: 每个batch维护beam_size个候选
        # 这里简化为batch_size=1的情况
        beams = [BeamCandidate(tokens=input_ids[0].tolist(), score=0.0)]
        
        # 存储已完成的序列
        completed = []
        
        for step in range(self.max_length):
            all_candidates = []
            
            for beam in beams:
                # 如果已经结束，加入completed列表
                if beam.tokens[-1] == self.eos_token_id:
                    completed.append(beam)
                    continue
                
                # 准备输入
                current_ids = torch.tensor([beam.tokens])
                
                # 获取模型输出
                with torch.no_grad():
                    logits = model_forward(current_ids)  # shape: (1, vocab_size)
                
                # 转为对数概率（数值更稳定）
                log_probs = F.log_softmax(logits[:, -1, :], dim=-1)
                
                # 获取top-k个候选
                top_k_log_probs, top_k_indices = torch.topk(
                    log_probs[0], 
                    min(self.beam_size, log_probs.size(-1))
                )
                
                # 扩展当前beam
                for i in range(len(top_k_log_probs)):
                    new_token = top_k_indices[i].item()
                    new_score = beam.score + top_k_log_probs[i].item()
                    new_tokens = beam.tokens + [new_token]
                    
                    all_candidates.append(
                        BeamCandidate(tokens=new_tokens, score=new_score)
                    )
            
            # 如果所有beam都已完成，退出
            if not all_candidates:
                break
            
            # 选择得分最高的beam_size个候选
            all_candidates.sort(reverse=True)  # 按得分降序
            beams = all_candidates[:self.beam_size]
            
            # 检查是否所有beam都到达结束符
            if all(b.tokens[-1] == self.eos_token_id for b in beams):
                completed.extend(beams)
                break
        
        # 将未完成的beam也加入结果
        completed.extend(beams)
        
        # 长度归一化得分
        final_results = []
        for candidate in completed:
            normalized_score = self._length_normalize(
                candidate.score, 
                len(candidate.tokens)
            )
            final_results.append((candidate.tokens, normalized_score))
        
        # 按归一化得分排序
        final_results.sort(key=lambda x: x[1], reverse=True)
        
        return final_results


def demonstrate_beam_search():
    """演示Beam Search的工作过程"""
    
    print("=" * 60)
    print("Beam Search演示")
    print("=" * 60)
    
    # 创建一个简单的模拟模型
    class MockModel:
        """模拟LLM模型"""
        def __init__(self, vocab_size: int = 100):
            self.vocab_size = vocab_size
            torch.manual_seed(42)
            # 创建一个转移概率矩阵（模拟）
            self.transition = torch.randn(vocab_size, vocab_size)
        
        def __call__(self, input_ids: torch.Tensor) -> torch.Tensor:
            """模拟前向传播"""
            # 使用最后一个token来决定下一个token的分布
            last_token = input_ids[0, -1].item()
            
            # 基于转移矩阵生成logits
            logits = self.transition[last_token].unsqueeze(0).unsqueeze(0)
            
            return logits
    
    # 创建模型和beam search
    model = MockModel(vocab_size=50)
    beam_search = BeamSearch(beam_size=3, max_length=10, eos_token_id=1)
    
    # 初始输入
    input_ids = torch.tensor([[10]])  # 起始token
    
    print(f"\n初始token: {input_ids[0].tolist()}")
    print(f"Beam大小: {beam_search.beam_size}")
    print(f"最大长度: {beam_search.max_length}")
    
    # 执行beam search
    results = beam_search.search(model, input_ids)
    
    print("\n--- Beam Search结果 (Top 5) ---")
    for i, (tokens, score) in enumerate(results[:5], 1):
        print(f"候选 {i}: tokens={tokens}, 归一化得分={score:.4f}")


def compare_greedy_vs_beam():
    """对比贪婪解码和Beam Search"""
    
    print("\n" + "=" * 60)
    print("贪婪解码 vs Beam Search 对比")
    print("=" * 60)
    
    # 创建模拟模型
    class SimpleModel:
        """简单的语言模型模拟"""
        def __call__(self, input_ids: torch.Tensor) -> torch.Tensor:
            torch.manual_seed(42 + len(input_ids[0]))  # 基于长度变化
            return torch.randn(1, 1, 50)  # vocab_size=50
    
    model = SimpleModel()
    input_ids = torch.tensor([[10]])
    
    # 贪婪解码
    print("\n--- 贪婪解码 ---")
    current = input_ids.clone()
    for _ in range(5):
        logits = model(current)
        next_token = torch.argmax(logits[0, -1]).unsqueeze(0).unsqueeze(0)
        current = torch.cat([current, next_token], dim=-1)
    print(f"结果: {current[0].tolist()}")
    
    # Beam Search
    print("\n--- Beam Search (beam_size=5) ---")
    beam_search = BeamSearch(beam_size=5, max_length=5)
    results = beam_search.search(model, input_ids)
    print(f"最佳结果: {results[0][0]}, 得分: {results[0][1]:.4f}")


if __name__ == "__main__":
    demonstrate_beam_search()
    compare_greedy_vs_beam()
