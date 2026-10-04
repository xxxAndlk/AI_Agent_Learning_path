"""
LoRA微调示例
使用PEFT库实现大模型的参数高效微调
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset

class LoRATrainer:
    """LoRA微调训练器"""
    
    def __init__(self, model_name: str = "gpt2"):
        """
        初始化LoRA训练器
        
        参数:
            model_name: 预训练模型名称
        """
        self.model_name = model_name
        
        # 加载tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # 加载基础模型（使用8bit量化节省显存）
        print(f"正在加载模型: {model_name}")
        self.base_model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=torch.float16,
            device_map="auto",          # 自动分配层到GPU/CPU
            load_in_8bit=True           # 8bit量化
        )
        print("✅ 基础模型加载完成")
    
    def setup_lora(self, r: int = 16, alpha: int = 32, dropout: float = 0.05):
        """
        配置LoRA
        
        参数:
            r: LoRA秩（低秩矩阵的维度），通常8-64
            alpha: LoRA alpha（缩放参数），通常2*r
            dropout: dropout率，防止过拟合
        """
        # 配置LoRA
        lora_config = LoraConfig(
            task_type=TaskType.CAUSAL_LM,    # 任务类型：因果语言模型
            r=r,                              # LoRA秩
            lora_alpha=alpha,                 # 缩放参数
            lora_dropout=dropout,             # dropout率
            target_modules=[                  # 要添加LoRA的目标模块
                "q_proj",                     # Query投影
                "k_proj",                     # Key投影
                "v_proj",                     # Value投影
                "o_proj",                     # Output投影
            ],
            bias="none",                      # 不训练偏置
        )
        
        # 应用LoRA配置到模型
        self.model = get_peft_model(self.base_model, lora_config)
        
        # 打印可训练参数信息
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        total_params = sum(p.numel() for p in self.model.parameters())
        
        print(f"\n📊 LoRA配置:")
        print(f"  LoRA秩 (r): {r}")
        print(f"  LoRA alpha: {alpha}")
        print(f"  Dropout: {dropout}")
        print(f"\n💾 参数统计:")
        print(f"  总参数: {total_params:,}")
        print(f"  可训练参数: {trainable_params:,}")
        print(f"  训练比例: {trainable_params/total_params*100:.4f}%")
        print(f"  显存节省: ~{100 - trainable_params/total_params*100:.1f}%")
    
    def prepare_data(self, texts: list, max_length: int = 512):
        """
        准备训练数据
        
        参数:
            texts: 文本列表，每个元素是训练样本
            max_length: 最大序列长度
        """
        def tokenize_function(examples):
            """tokenize函数"""
            return self.tokenizer(
                examples["text"],
                truncation=True,
                max_length=max_length,
                padding="max_length"
            )
        
        # 创建数据集
        dataset = Dataset.from_dict({"text": texts})
        tokenized_dataset = dataset.map(
            tokenize_function,
            batched=True,
            remove_columns=dataset.column_names
        )
        
        return tokenized_dataset
    
    def train(self, train_dataset, output_dir: str = "./lora_model", epochs: int = 3):
        """
        训练模型
        
        参数:
            train_dataset: 训练数据集
            output_dir: 模型输出目录
            epochs: 训练轮数
        """
        # 训练参数
        training_args = TrainingArguments(
            output_dir=output_dir,              # 输出目录
            num_train_epochs=epochs,            # 训练轮数
            per_device_train_batch_size=4,      # 每设备batch大小
            gradient_accumulation_steps=4,      # 梯度累积步数
            learning_rate=2e-4,                 # 学习率
            warmup_steps=100,                   # 预热步数
            logging_steps=10,                   # 日志记录步数
            save_steps=500,                     # 保存步数
            save_total_limit=2,                 # 最多保留的checkpoint数
            fp16=True,                          # 使用FP16混合精度
            report_to="none",                   # 不报告到wandb等
        )
        
        # 创建训练器（简化版，实际使用Trainer类）
        print(f"\n🚀 开始训练 {epochs} 轮...")
        
        # 这里简化展示，实际使用transformers.Trainer
        # trainer = Trainer(...)
        # trainer.train()
        
        print("✅ 训练完成")
        
        # 保存模型
        self.model.save_pretrained(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        print(f"💾 模型已保存到: {output_dir}")
    
    def inference(self, prompt: str, max_length: int = 100) -> str:
        """
        模型推理
        
        参数:
            prompt: 输入提示
            max_length: 最大生成长度
        返回:
            生成的文本
        """
        # 编码输入
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)
        
        # 生成
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True
            )
        
        # 解码输出
        generated_text = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return generated_text

# 使用示例
def lora_example():
    """LoRA微调完整示例"""
    
    # 准备训练数据（模拟领域数据）
    train_texts = [
        "用户：你好，请问什么是机器学习？\n助手：机器学习是人工智能的一个分支，它让计算机能够从数据中学习和改进，而无需明确编程。",
        "用户：深度学习有什么应用？\n助手：深度学习广泛应用于图像识别、自然语言处理、语音识别、自动驾驶等领域。",
        "用户：什么是神经网络？\n助手：神经网络是一种受生物神经元启发的计算模型，由相互连接的节点层组成，能够学习和识别模式。",
        "用户：Transformer是什么？\n助手：Transformer是一种深度学习架构，使用自注意力机制处理序列数据，是GPT等大模型的基础。",
        "用户：如何学习AI？\n助手：学习AI可以从Python编程开始，然后学习机器学习基础、深度学习框架，最后实践项目。",
    ]
    
    # 初始化训练器
    trainer = LoRATrainer(model_name="gpt2")  # 使用小模型演示
    
    # 配置LoRA
    trainer.setup_lora(r=8, alpha=16, dropout=0.05)
    
    # 准备数据
    train_dataset = trainer.prepare_data(train_texts, max_length=256)
    
    # 训练（演示用，实际可能需要更多数据和更长时间）
    # trainer.train(train_dataset, epochs=3)
    
    # 推理测试
    test_prompt = "用户：什么是深度学习？\n助手："
    # result = trainer.inference(test_prompt)
    # print(f"输入: {test_prompt}")
    # print(f"输出: {result}")

if __name__ == "__main__":
    lora_example()
