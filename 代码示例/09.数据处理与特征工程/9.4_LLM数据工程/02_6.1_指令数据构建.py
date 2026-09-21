import json                              # JSON处理库，用于数据序列化
from typing import List, Dict, Optional  # 类型提示
from dataclasses import dataclass        # 数据类装饰器

# ============ 数据格式定义 ============

@dataclass
class AlpacaFormat:
    """Alpaca格式指令数据
    
    最常用的指令数据格式，结构简单清晰
    包含三个字段：instruction（指令）、input（输入上下文）、output（期望输出）
    """
    instruction: str                      # 指令：描述任务要求
    input: str = ""                       # 输入：可选的上下文信息
    output: str = ""                      # 输出：期望的模型回复
    
    def to_dict(self) -> Dict:
        """转换为字典格式，便于JSON序列化"""
        return {
            "instruction": self.instruction,    # 将instruction转为字典键
            "input": self.input,                 # 将input转为字典键
            "output": self.output                # 将output转为字典键
        }


@dataclass
class ShareGPTFormat:
    """ShareGPT格式指令数据
    
    支持多轮对话的格式，使用conversations字段存储对话历史
    每条消息包含from（发送者）和value（内容）两个字段
    """
    conversations: List[Dict]             # 对话列表，每项包含from和value
    source: str = "human"                 # 数据来源标识
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "conversations": self.conversations,  # 对话历史
            "source": self.source                  # 数据来源
        }


class InstructionDataBuilder:
    """指令数据构建器
    
    提供多种方法来构建、转换和验证指令数据
    """
    
    @staticmethod
    def build_alpaca_data(
        instruction: str,
        output: str,
        input_context: str = ""
    ) -> Dict:
        """构建Alpaca格式的单条指令数据
        
        参数:
            instruction: 任务指令描述
            output: 期望的输出
            input_context: 可选的输入上下文
        返回:
            Alpaca格式的字典
        """
        # 创建Alpaca格式对象并转换为字典
        data = AlpacaFormat(
            instruction=instruction,      # 设置指令内容
            input=input_context,          # 设置输入上下文（可为空）
            output=output                 # 设置期望输出
        )
        return data.to_dict()             # 返回字典格式
    
    @staticmethod
    def build_sharegpt_data(
        conversation_pairs: List[tuple]
    ) -> Dict:
        """构建ShareGPT格式的多轮对话数据
        
        参数:
            conversation_pairs: 对话对列表，如 [("user", "问题"), ("assistant", "回答")]
        返回:
            ShareGPT格式的字典
        """
        conversations = []
        # 遍历对话对，构建conversations列表
        for role, content in conversation_pairs:
            # 将角色映射为ShareGPT格式
            # "user" -> "human", "assistant" -> "gpt"
            mapped_role = "human" if role == "user" else "gpt"
            conversations.append({
                "from": mapped_role,      # 发送者角色
                "value": content          # 消息内容
            })
        
        data = ShareGPTFormat(conversations=conversations)  # 创建ShareGPT格式对象
        return data.to_dict()             # 返回字典格式
    
    @staticmethod
    def convert_alpaca_to_sharegpt(alpaca_data: Dict) -> Dict:
        """将Alpaca格式转换为ShareGPT格式
        
        参数:
            alpaca_data: Alpaca格式的数据字典
        返回:
            ShareGPT格式的数据字典
        """
        # 构建用户消息：如果有input则拼接
        user_message = alpaca_data["instruction"]  # 获取指令
        if alpaca_data.get("input"):
            # 如果有输入上下文，将其附加到指令后
            user_message += f"\n{alpaca_data['input']}"
        
        # 构建对话对：用户消息 + 助手回复
        conversation_pairs = [
            ("user", user_message),                # 用户消息
            ("assistant", alpaca_data["output"])   # 助手回复
        ]
        
        # 调用build_sharegpt_data构建ShareGPT格式
        return InstructionDataBuilder.build_sharegpt_data(conversation_pairs)


def create_sample_instruction_dataset():
    """创建示例指令数据集
    
    演示如何构建不同格式的指令数据
    """
    # ============ 示例1：Alpaca格式 ============
    print("=" * 50)
    print("示例1：Alpaca格式指令数据")
    print("=" * 50)
    
    alpaca_samples = [
        # 无输入上下文的简单指令
        InstructionDataBuilder.build_alpaca_data(
            instruction="解释什么是机器学习",
            output="机器学习是人工智能的一个分支，它使计算机系统能够从数据中学习并改进，而无需明确编程。"
        ),
        # 带输入上下文的指令
        InstructionDataBuilder.build_alpaca_data(
            instruction="将以下句子翻译成英文",
            input_context="人工智能正在改变我们的生活方式。",
            output="Artificial intelligence is changing the way we live."
        ),
    ]
    
    # 打印Alpaca格式数据
    for i, sample in enumerate(alpaca_samples, 1):
        print(f"\n--- 样本 {i} ---")
        print(json.dumps(sample, ensure_ascii=False, indent=2))
    
    # ============ 示例2：ShareGPT格式 ============
    print("\n" + "=" * 50)
    print("示例2：ShareGPT格式多轮对话数据")
    print("=" * 50)
    
    # 多轮对话示例
    multi_turn_conversation = [
        ("user", "什么是RAG技术？"),
        ("assistant", "RAG是一种结合检索和生成的技术。"),
        ("user", "RAG有什么优势？"),
        ("assistant", "主要优势包括减少幻觉、知识可更新、可追溯来源。"),
    ]
    
    # 构建ShareGPT格式数据
    sharegpt_data = InstructionDataBuilder.build_sharegpt_data(multi_turn_conversation)
    print(json.dumps(sharegpt_data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    create_sample_instruction_dataset()
