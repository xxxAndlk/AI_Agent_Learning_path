"""
混合精度训练实现
"""

import torch
import torch.nn as nn
from transformers import AutoModelForCausalLM, TrainingArguments


# ============================================================
# 方法1：使用PyTorch原生AMP
# ============================================================

def pytorch_amp_example():
    """使用PyTorch的自动混合精度"""
    
    # 创建模型
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    
    # 创建优化器
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    
    # 创建GradScaler
    scaler = torch.amp.GradScaler("cuda")
    
    # 训练循环
    model.train()
    for batch in dataloader:
        optimizer.zero_grad()
        
        # 自动混合精度上下文
        with torch.amp.autocast("cuda", dtype=torch.float16):
            outputs = model(**batch)
            loss = outputs.loss
        
        # 反向传播（缩放后的loss）
        scaler.scale(loss).backward()
        
        # 梯度裁剪
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        
        # 参数更新
        scaler.step(optimizer)
        scaler.update()


# ============================================================
# 方法2：使用Transformers Trainer
# ============================================================

def transformers_amp_example():
    """使用Transformers的Trainer进行混合精度训练"""
    
    from transformers import Trainer, TrainingArguments
    
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    
    training_args = TrainingArguments(
        output_dir="./output",
        
        # 启用FP16混合精度
        fp16=True,  # 对于NVIDIA GPU
        
        # 或者使用BF16 (Ampere或更新架构)
        # bf16=True,
        
        # 训练参数
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
    )
    
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
    )
    
    trainer.train()


# ============================================================
# BF16 vs FP16 选择
# ============================================================

def bf16_vs_fp16():
    """BF16和FP16的选择建议"""
    
    # BF16 优势：
    # - 动态范围更大，不容易溢出
    # - 不需要损失缩放
    # - 训练更稳定
    # 
    # FP16 优势：
    # - 更广泛的硬件支持
    # - 精度稍高（对于某些任务）
    
    # 选择依据
    if torch.cuda.is_available():
        # Ampere架构或更新：推荐BF16
        if torch.cuda.get_device_capability()[0] >= 8:
            return "bf16"
        else:
            return "fp16"
    
    return "fp32"  # 老旧GPU


# ============================================================
# 方法3：DeepSpeed集成
# ============================================================

def deepspeed_amp_example():
    """使用DeepSpeed进行混合精度训练"""
    
    # ds_config.json
    ds_config = {
        "train_batch_size": 8,
        "gradient_accumulation_steps": 4,
        "steps_per_print": 10,
        "fp16": {
            "enabled": True,
            "loss_scale": 0,
            "loss_scale_window": 1000,
            "initial_scale_power": 16,
            "hysteresis": 2,
            "min_loss_scale": 1
        },
        # 或者使用BF16
        # "bf16": {
        #     "enabled": True
        # },
        "zero_optimization": {
            "stage": 2,
            "offload_optimizer": {
                "device": "cpu",
                "pin_memory": True
            },
            "allgather_partitions": True,
            "allgather_bucket_size": 5e8,
            "overlap_comm": True,
            "reduce_scatter": True,
            "reduce_bucket_size": 5e8,
            "contiguous_gradients": True
        }
    }
    
    # 使用
    # training_args = TrainingArguments(
    #     output_dir="./output",
    #     deepspeed="./ds_config.json",
    # )
    
    return ds_config


# ============================================================
# 梯度累积与混合精度
# ============================================================

def gradient_accumulation_with_amp():
    """梯度累积与混合精度结合"""
    
    # 关键点：GradScaler需要根据累积步数调整
    # 但实际不需要手动调整，scaler会自动处理
    
    scaler = torch.amp.GradScaler("cuda")
    gradient_accumulation_steps = 4
    
    model.train()
    for step, batch in enumerate(dataloader):
        # 自动混合精度前向
        with torch.amp.autocast("cuda", dtype=torch.float16):
            outputs = model(**batch)
            loss = outputs.loss / gradient_accumulation_steps
        
        # 缩放后的反向传播
        scaler.scale(loss).backward()
        
        # 累积步数到达时更新参数
        if (step + 1) % gradient_accumulation_steps == 0:
            # 梯度裁剪
            scaler.unscale_(optimizer)
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            
            # 参数更新
            scaler.step(optimizer)
            scaler.update()
            optimizer.zero_grad()


# ============================================================
# 验证混合精度是否正常工作
# ============================================================

def verify_amp_working():
    """验证AMP是否正常工作"""
    
    # 检查CUDA是否支持
    print(f"CUDA可用: {torch.cuda.is_available()}")
    
    # 检查设备计算能力
    if torch.cuda.is_available():
        print(f"GPU名称: {torch.cuda.get_device_name(0)}")
        print(f"计算能力: {torch.cuda.get_device_capability(0)}")
    
    # 简单测试
    model = AutoModelForCausalLM.from_pretrained("gpt2").cuda()
    batch = {"input_ids": torch.randint(0, 50257, (2, 32)).cuda()}
    
    with torch.amp.autocast("cuda", dtype=torch.float16):
        outputs = model(**batch)
    
    print(f"输出类型: {outputs.logits.dtype}")
    # 应该显示 torch.float16
    
    return outputs.logits.dtype == torch.float16
