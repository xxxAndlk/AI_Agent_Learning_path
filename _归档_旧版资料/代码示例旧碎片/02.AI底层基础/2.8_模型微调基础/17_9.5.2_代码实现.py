"""
Gradient Checkpointing实现
"""

import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, AutoTokenizer
from torch.utils.checkpoint import checkpoint_sequential


# ============================================================
# 方法1：使用Transformers库的Gradient Checkpointing
# ============================================================

def gradient_checkpointing_transformers():
    """在Transformers模型中启用Gradient Checkpointing"""
    
    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        "gpt2",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 启用Gradient Checkpointing
    # 对于CausalLM模型，使用enable_gradient_checkpointing()
    model.gradient_checkpointing_enable()
    
    # 对于Encoder-Decoder模型
    # model.gradient_checkpointing_enable(gradient_checkpointing_func=checkpoint)
    
    # 验证是否启用
    if hasattr(model, 'gradient_checkpointing'):
        print("Gradient Checkpointing已启用")
    
    # 训练时显存对比：
    # 7B模型：约28GB → 约14GB（取决于配置）
    return model


def disable_gradient_checkpointing():
    """禁用Gradient Checkpointing"""
    model.gradient_checkpointing_disable()


# ============================================================
# 方法2：手动实现Gradient Checkpointing
# ============================================================

class CheckpointedBlock(nn.Module):
    """带有Gradient Checkpointing的模块"""
    
    def __init__(self, module, use_checkpoint=True, checkpoint_ratio=1):
        super().__init__()
        self.module = module
        self.use_checkpoint = use_checkpoint
        self.checkpoint_ratio = checkpoint_ratio
    
    def forward(self, x):
        if self.use_checkpoint and self.training:
            # 使用gradient checkpointing
            return torch.utils.checkpoint.checkpoint(
                self.module,
                x,
                use_reentrant=False  # 新版本推荐
            )
        else:
            return self.module(x)


def apply_gradient_checkpointing_to_model(model, use_checkpoint=True):
    """
    为模型应用Gradient Checkpointing
    
    遍历模型的所有层，对每个块应用checkpoint
    """
    for name, module in model.named_modules():
        # 检查是否是transformer层
        if "transformer_layer" in name or "attention" in name.lower():
            # 可以选择性应用checkpoint
            # 例如：每隔一层应用一次
            parent_name = ".".join(name.split(".")[:-1])
            if parent_name:
                parent = model.get_submodule(parent_name)
                child_name = name.split(".")[-1]
                
                # 替换为checkpointed版本
                # 实际实现需要更复杂的逻辑
                pass
    
    return model


# ============================================================
# 方法3：在自定义模型中使用
# ============================================================

class CustomModelWithCheckpoint(nn.Module):
    """演示如何在自定义模型中使用Gradient Checkpointing"""
    
    def __init__(self, hidden_size, num_layers):
        super().__init__()
        self.layers = nn.ModuleList([
            nn.Sequential(
                nn.Linear(hidden_size, hidden_size),
                nn.ReLU(),
                nn.Linear(hidden_size, hidden_size),
            )
            for _ in range(num_layers)
        ])
    
    def forward(self, x):
        # 方法1：使用checkpoint_sequential
        # 将层分组，每组作为一个checkpoint
        num_layers = len(self.layers)
        checkpointed_layers = nn.ModuleList([
            self.layers[i] for i in range(num_layers)
        ])
        
        # 分组checkpoint
        # 假设我们想分成3组
        groups = 3
        layers_per_group = num_layers // groups
        
        hidden = x
        for i in range(0, num_layers, layers_per_group):
            group_layers = self.layers[i:i + layers_per_group]
            if self.training:
                # 使用checkpoint
                hidden = checkpoint_sequential(
                    group_modules=group_layers,
                    num_segments=len(group_layers),
                    input=hidden
                )
            else:
                # 推理时正常计算
                for layer in group_layers:
                    hidden = layer(hidden)
        
        return hidden


# ============================================================
# 与其他显存优化技术结合
# ============================================================

def combined_optimization_example():
    """组合多种显存优化技术"""
    
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        torch_dtype=torch.float16,
        device_map="auto",
        # 使用8bit量化
        load_in_8bit=True,
    )
    
    # 1. 启用Gradient Checkpointing
    model.gradient_checkpointing_enable()
    
    # 2. 使用LoRA（已有）
    from peft import LoraConfig, get_peft_model
    lora_config = LoraConfig(r=16, lora_alpha=32)
    model = get_peft_model(model, lora_config)
    
    # 显存对比（7B模型）：
    # 基础: ~28GB
    # + 8bit: ~14GB
    # + Gradient Checkpointing: ~7GB
    # + LoRA: ~5GB
    
    return model


# ============================================================
# 配置参数调优
# ============================================================

def training_args_with_checkpoint():
    """TrainingArguments中的Gradient Checkpointing配置"""
    
    from transformers import TrainingArguments
    
    training_args = TrainingArguments(
        output_dir="./output",
        per_device_train_batch_size=1,
        gradient_accumulation_steps=16,  # 增大以补偿小batch
        learning_rate=2e-4,
        
        # Gradient Checkpointing相关
        # transformers库会自动启用
        # 但可以控制检查点频率
        # 
        # 注意：在transformers 4.36+版本中
        # gradient_checkpointing_enable() 有额外参数
        #
        # 使用use_reentrant=False (推荐)
    )
    
    return training_args
