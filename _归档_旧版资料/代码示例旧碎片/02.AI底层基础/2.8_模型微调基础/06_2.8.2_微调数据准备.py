"""
微调数据准备示例
展示如何准备指令格式的微调数据
"""

import json
from typing import List, Dict

class InstructionDataFormatter:
    """指令数据格式化器"""
    
    def __init__(self, system_prompt: str = ""):
        """
        初始化格式化器
        
        参数:
            system_prompt: 系统提示词
        """
        self.system_prompt = system_prompt
    
    def format_alpaca(self, instruction: str, input_text: str = "", output: str = "") -> str:
        """
        Alpaca格式
        格式：instruction + input -> output
        """
        if input_text:
            prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n{output}"
        else:
            prompt = f"### Instruction:\n{instruction}\n\n### Response:\n{output}"
        return prompt
    
    def format_chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Chat格式（类OpenAI格式）
        格式：[{"role": "user", "content": "..."}, ...]
        """
        formatted = ""
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                formatted += f"<|system|>\n{content}\n"
            elif role == "user":
                formatted += f"<|user|>\n{content}\n"
            elif role == "assistant":
                formatted += f"<|assistant|>\n{content}\n"
        return formatted
    
    def format_sharegpt(self, conversations: List[Dict[str, str]]) -> str:
        """
        ShareGPT格式（多轮对话）
        """
        formatted = ""
        for turn in conversations:
            if turn["from"] == "human":
                formatted += f"Human: {turn['value']}\n\n"
            elif turn["from"] == "gpt":
                formatted += f"Assistant: {turn['value']}\n\n"
        return formatted.strip()
    
    def create_instruction_dataset(self, raw_data: List[Dict], format_type: str = "alpaca") -> List[str]:
        """
        创建指令数据集
        
        参数:
            raw_data: 原始数据列表
            format_type: 格式类型 (alpaca/chat/sharegpt)
        返回:
            格式化后的文本列表
        """
        formatted_data = []
        
        for item in raw_data:
            if format_type == "alpaca":
                text = self.format_alpaca(
                    instruction=item.get("instruction", ""),
                    input_text=item.get("input", ""),
                    output=item.get("output", "")
                )
            elif format_type == "chat":
                text = self.format_chat(item.get("messages", []))
            elif format_type == "sharegpt":
                text = self.format_sharegpt(item.get("conversations", []))
            else:
                text = str(item)
            
            formatted_data.append(text)
        
        return formatted_data
    
    def save_dataset(self, data: List[str], filepath: str):
        """保存数据集到文件"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps({"text": item}, ensure_ascii=False) + "\n")
        print(f"✅ 数据集已保存到: {filepath}")

# 使用示例
if __name__ == "__main__":
    formatter = InstructionDataFormatter()
    
    # 示例数据
    raw_data = [
        {
            "instruction": "解释什么是机器学习",
            "input": "",
            "output": "机器学习是人工智能的一个分支，它使计算机能够从数据中学习而无需明确编程。"
        },
        {
            "instruction": "翻译以下句子",
            "input": "Hello, how are you?",
            "output": "你好，你好吗？"
        }
    ]
    
    # 格式化
    formatted = formatter.create_instruction_dataset(raw_data, format_type="alpaca")
    
    print("格式化后的数据示例:")
    for i, text in enumerate(formatted[:2], 1):
        print(f"\n--- 样本 {i} ---")
        print(text[:200] + "..." if len(text) > 200 else text)
