"""
Token生成过程示例
展示LLM自回归生成文本的核心机制
"""

import torch                        # PyTorch深度学习框架
import torch.nn.functional as F     # 神经网络函数模块
from typing import List, Optional   # 类型提示

class SimpleTokenGenerator:
    """简单的Token生成器
    
    模拟LLM的自回归生成过程
    """
    
    def __init__(self, vocab_size: int = 1000, hidden_size: int = 256):
        """
        初始化生成器
        
        参数:
            vocab_size: 词汇表大小
            hidden_size: 隐藏层维度
        """
        self.vocab_size = vocab_size                # 词汇表大小
        self.hidden_size = hidden_size              # 隐藏层维度
        
        # 创建简单的线性层模拟模型的输出层
        # 实际LLM中这是一个复杂的Transformer网络
        self.embedding = torch.nn.Embedding(vocab_size, hidden_size)   # 词嵌入层
        self.output_layer = torch.nn.Linear(hidden_size, vocab_size)   # 输出层，映射到词汇表
        
    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """
        前向传播：计算下一个token的概率分布
        
        参数:
            input_ids: 输入token ID序列，shape: (batch_size, seq_len)
        返回:
            logits: 每个位置对所有词汇的得分，shape: (batch_size, seq_len, vocab_size)
        """
        # 获取词嵌入
        embeddings = self.embedding(input_ids)      # shape: (batch, seq_len, hidden)
        
        # 简化的"模型"处理：取最后一个位置的嵌入
        # 实际LLM会经过多层Transformer，使用注意力机制聚合信息
        last_hidden = embeddings[:, -1, :]          # shape: (batch, hidden)
        
        # 计算logits（未归一化的概率）
        logits = self.output_layer(last_hidden)     # shape: (batch, vocab_size)
        
        return logits
    
    def generate_next_token(
        self, 
        input_ids: torch.Tensor, 
        temperature: float = 1.0
    ) -> torch.Tensor:
        """
        生成下一个token
        
        参数:
            input_ids: 当前输入序列
            temperature: 温度参数，控制随机性
        返回:
            next_token: 生成的下一个token ID
        """
        # 获取logits
        logits = self.forward(input_ids)            # shape: (batch, vocab_size)
        
        # 应用温度缩放
        # temperature > 1: 更随机，temperature < 1: 更确定
        scaled_logits = logits / temperature
        
        # 转换为概率分布（Softmax）
        probs = F.softmax(scaled_logits, dim=-1)    # shape: (batch, vocab_size)
        
        # 从概率分布中采样
        next_token = torch.multinomial(probs, num_samples=1)  # shape: (batch, 1)
        
        return next_token
    
    def generate(
        self, 
        prompt_ids: torch.Tensor, 
        max_new_tokens: int = 50,
        temperature: float = 1.0,
        eos_token_id: Optional[int] = None
    ) -> torch.Tensor:
        """
        自回归生成多个token
        
        这是LLM生成的核心循环：每次生成一个token，加入序列，继续生成
        
        参数:
            prompt_ids: 输入提示的token ID，shape: (1, prompt_len)
            max_new_tokens: 最大生成token数
            temperature: 采样温度
            eos_token_id: 结束符token ID，遇到则停止
        返回:
            generated_ids: 生成的完整序列
        """
        generated_ids = prompt_ids.clone()          # 复制输入序列
        
        print(f"🔍 开始自回归生成，初始序列长度: {generated_ids.shape[1]}")
        
        for step in range(max_new_tokens):
            # 核心步骤：预测下一个token
            next_token = self.generate_next_token(generated_ids, temperature)
            
            # 将新token拼接到序列末尾
            generated_ids = torch.cat([generated_ids, next_token], dim=-1)
            
            # 打印生成过程
            print(f"  Step {step+1}: 生成token ID={next_token.item()}")
            
            # 检查是否遇到结束符
            if eos_token_id is not None and next_token.item() == eos_token_id:
                print(f"✅ 遇到结束符，停止生成")
                break
        
        print(f"📝 生成完成，最终序列长度: {generated_ids.shape[1]}")
        return generated_ids


def demonstrate_autoregressive_generation():
    """演示自回归生成过程"""
    
    print("=" * 60)
    print("LLM自回归生成原理演示")
    print("=" * 60)
    
    # 创建生成器
    generator = SimpleTokenGenerator(vocab_size=100, hidden_size=64)
    
    # 模拟输入序列（实际应用中由Tokenizer生成）
    # 假设词汇表：0=<pad>, 1=<eos>, 2=<unk>, 10-99是实际词汇
    prompt_ids = torch.tensor([[10, 25, 37, 42]])  # shape: (1, 4)
    
    print(f"\n输入序列: {prompt_ids.tolist()}")
    print(f"含义（假设）: ['今', '天', '天', '气']\n")
    
    # 生成新token
    output_ids = generator.generate(
        prompt_ids,
        max_new_tokens=10,
        temperature=0.8,
        eos_token_id=1
    )
    
    print(f"\n输出序列: {output_ids.tolist()}")


if __name__ == "__main__":
    demonstrate_autoregressive_generation()
