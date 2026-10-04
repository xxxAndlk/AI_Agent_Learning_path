"""
多任务微调实现
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from datasets import Dataset, DatasetDict
from collections import defaultdict
import random


# ============================================================
# 方法1：数据混合
# ============================================================

def prepare_multi_task_dataset():
    """准备多任务数据集"""
    
    # 定义任务数据
    tasks_data = {
        "classification": [
            {"instruction": "判断这段文本的情感", "input": "今天天气真好", "output": "positive"},
            {"instruction": "判断这段文本的情感", "input": "太糟糕了", "output": "negative"},
        ],
        "qa": [
            {"instruction": "回答问题", "input": "什么是机器学习？", "output": "机器学习是..."},
            {"instruction": "回答问题", "input": "水的化学式是什么？", "output": "H2O"},
        ],
        "generation": [
            {"instruction": "写一首诗", "input": "春天", "output": "春风拂面..."},
        ],
    }
    
    # 混合数据（可以加权）
    mixed_data = []
    
    # 方案1：均匀采样
    for task_name, data in tasks_data.items():
        mixed_data.extend(data)
    
    # 方案2：加权采样（根据数据量）
    weights = {"classification": 0.4, "qa": 0.4, "generation": 0.2}
    for task_name, data in tasks_data.items():
        weight = weights.get(task_name, 1.0)
        sampled = random.choices(data, k=int(len(data) * weight / min(weights.values())))
        mixed_data.extend(sampled)
    
    random.shuffle(mixed_data)
    return mixed_data


# ============================================================
# 方法2：任务平衡采样
# ============================================================

class TaskBalancedSampler:
    """任务平衡采样器"""
    
    def __init__(self, task_datasets, tasks_per_batch=1):
        """
        参数:
            task_datasets: dict[任务名 -> 数据集]
            tasks_per_batch: 每个batch包含的任务数
        """
        self.task_datasets = task_datasets
        self.tasks_per_batch = tasks_per_batch
        self.task_iterators = {
            name: iter(data) 
            for name, data in task_datasets.items()
        }
    
    def __iter__(self):
        task_names = list(self.task_datasets.keys())
        
        while True:
            # 随机选择任务
            selected_tasks = random.sample(task_names, self.tasks_per_batch)
            batch = []
            
            for task_name in selected_tasks:
                # 尝试从该任务获取样本
                try:
                    sample = next(self.task_iterators[task_name])
                    sample["task"] = task_name  # 标记任务
                    batch.append(sample)
                except StopIteration:
                    # 重置迭代器
                    self.task_iterators[task_name] = iter(self.task_datasets[task_name])
            
            if batch:
                yield batch
    
    def __len__(self):
        return min(len(data) for data in self.task_datasets.values())


# ============================================================
# 方法3：指令微调格式统一
# ============================================================

def format_multi_task_data(task_name, instruction, input_text, output):
    """统一格式化多任务数据"""
    
    # 方案1：添加任务前缀
    if task_name == "classification":
        prompt = f"""[情感分类] {instruction}
输入: {input_text}
输出: {output}"""
    
    elif task_name == "qa":
        prompt = f"""[问答] {instruction}
问题: {input_text}
答案: {output}"""
    
    elif task_name == "generation":
        prompt = f"""[文本生成] {instruction}
主题: {input_text}
生成: {output}"""
    
    else:
        prompt = f"""任务: {task_name}
{instruction}
{input_text}
输出: {output}"""
    
    return prompt


def create_unified_instruction_dataset(tasks_data, tokenizer, max_length=512):
    """创建统一指令格式的数据集"""
    
    all_data = []
    
    for task_name, examples in tasks_data.items():
        for example in examples:
            formatted = format_multi_task_data(
                task_name,
                example["instruction"],
                example.get("input", ""),
                example["output"]
            )
            
            # Tokenize
            tokens = tokenizer(
                formatted,
                max_length=max_length,
                truncation=True,
                padding="max_length",
                return_tensors="pt"
            )
            
            all_data.append({
                "input_ids": tokens["input_ids"].squeeze(),
                "attention_mask": tokens["attention_mask"].squeeze(),
                "labels": tokens["input_ids"].squeeze(),
                "task": task_name,
            })
    
    return Dataset.from_list(all_data)


# ============================================================
# 方法4：任务向量
# ============================================================

class MultiTaskTrainer:
    """多任务训练器"""
    
    def __init__(self, model, tasks, task_weights=None):
        self.model = model
        self.tasks = tasks
        # 任务权重（可以动态调整）
        self.task_weights = task_weights or {t: 1.0 for t in tasks}
    
    def compute_task_loss(self, outputs, task_name, labels):
        """计算单个任务的损失"""
        
        # 不同任务可能使用不同的损失函数
        if task_name == "classification":
            # 分类任务：交叉熵
            loss = torch.nn.functional.cross_entropy(
                outputs.logits.view(-1, outputs.logits.size(-1)),
                labels.view(-1)
            )
        else:
            # 生成任务：自回归损失
            # Transformers库已计算
            loss = outputs.loss
        
        return loss
    
    def train_step(self, batch):
        """单步训练"""
        
        total_loss = 0
        task_losses = {}
        
        for task_name in self.tasks:
            if task_name in batch:
                task_batch = {k: v for k, v in batch.items() if k != "task"}
                task_batch["labels"] = batch[task_name]["labels"]
                
                outputs = self.model(**task_batch)
                task_loss = self.compute_task_loss(outputs, task_name, task_batch["labels"])
                
                # 应用任务权重
                weighted_loss = task_loss * self.task_weights[task_name]
                
                total_loss += weighted_loss
                task_losses[task_name] = task_loss.item()
        
        # 反向传播
        total_loss.backward()
        
        return total_loss.item(), task_losses


# ============================================================
# 方法5：动态任务权重
# ============================================================

class DynamicTaskWeighting:
    """动态任务权重调整"""
    
    def __init__(self, tasks, initial_weights=None, method="gradnorm"):
        self.tasks = tasks
        self.weights = initial_weights or {t: 1.0 for t in tasks}
        self.method = method
        
        # 记录每个任务的梯度范数
        self.grad_norms = {t: [] for t in tasks}
    
    def update_weights(self, grad_norms, epoch):
        """根据梯度范数更新任务权重"""
        
        if self.method == "gradnorm":
            # GradNorm：平衡不同任务的梯度范数
            avg_grad = sum(grad_norms.values()) / len(grad_norms)
            
            for task in self.tasks:
                # 权重与梯度范数成反比
                self.weights[task] = avg_grad / (grad_norms[task] + 1e-8)
        
        elif self.method == "uncertainty":
            # 基于任务不确定性调整
            # 简单实现：减少损失大的任务的权重
            pass
        
        elif self.method == "decay":
            # 简单衰减：逐渐减少权重
            decay_rate = 0.95 ** epoch
            for task in self.tasks:
                self.weights[task] *= decay_rate
        
        # 归一化
        total = sum(self.weights.values())
        for task in self.tasks:
            self.weights[task] /= total
        
        return self.weights


# ============================================================
# 完整的多任务微调示例
# ============================================================

def multi_task_finetuning_example():
    """完整的多任务微调示例"""
    
    from transformers import Trainer, TrainingArguments
    from peft import LoraConfig, get_peft_model
    
    # 1. 准备数据
    tasks_data = {
        "sentiment": load_sentiment_data(),
        "qa": load_qa_data(),
        "summarization": load_summarization_data(),
        "translation": load_translation_data(),
    }
    
    # 2. 统一格式化
    dataset = create_unified_instruction_dataset(
        tasks_data, 
        tokenizer, 
        max_length=512
    )
    
    # 3. 加载模型（使用LoRA）
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    lora_config = LoraConfig(r=16, lora_alpha=32)
    model = get_peft_model(model, lora_config)
    
    # 4. 训练配置
    training_args = TrainingArguments(
        output_dir="./multi_task_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=2e-4,
        
        # 数据采样
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        
        # 保存和评估
        save_steps=500,
        eval_steps=500,
        
        # 混合精度
        fp16=True,
    )
    
    # 5. 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
    )
    
    trainer.train()
    
    return model
