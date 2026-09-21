"""
DPO训练实现
使用TRL库的DPOTrainer
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import DPOTrainer, DPOConfig
from peft import LoraConfig
from datasets import Dataset

# ============================================================
# DPO数据准备
# ============================================================

def prepare_dpo_dataset(preference_data):
    """
    准备DPO训练数据
    每个样本包含：prompt, chosen（优选response）, rejected（差选response）
    
    数据格式：
    [
        {
            "prompt": "用户问题...",
            "chosen": "好的回答...",
            "rejected": "差的回答..."
        },
        ...
    ]
    """
    dataset = Dataset.from_list(preference_data)
    return dataset


# ============================================================
# DPO训练
# ============================================================

def dpo_training_example():
    """DPO训练示例"""
    
    # 加载基础模型
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
    
    # 参考模型（用于KL正则）
    ref_model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 配置LoRA
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
        lora_dropout=0.05,
        task_type="CAUSAL_LM"
    )
    
    # DPO配置
    dpo_config = DPOConfig(
        # 训练参数
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=1e-5,
        lr_scheduler_type="cosine",
        warmup_ratio=0.1,
        weight_decay=0.01,
        
        # DPO特定参数
        beta=0.1,  # KL正则系数，通常0.1~0.5
        loss_type="sigmoid",  # 或 "hinge"
        
        # 生成参数（用于构建batch）
        max_length=512,
        max_prompt_length=256,
        max_target_length=256,
        
        # 掩码
        is_encoder_decoder=False,
        pad_token_id=tokenizer.pad_token_id,
        
        # 日志和保存
        logging_steps=10,
        save_steps=500,
        output_dir="./dpo_output",
        
        # 精度
        fp16=True,
        remove_unused_columns=False,
    )
    
    # DPO训练器
    dpo_trainer = DPOTrainer(
        model=model,
        ref_model=ref_model,  # 参考模型
        args=dpo_config,
        train_dataset=train_dataset,  # 偏好数据集
        eval_dataset=eval_dataset,
        tokenizer=tokenizer,
        peft_config=lora_config,
        
        # 数据处理
        dataset_num_proc=4,
        processing_class=tokenizer,
    )
    
    # 开始训练
    dpo_trainer.train()
    
    # 保存模型
    dpo_trainer.save_model("./dpo_model")
    dpo_trainer.save_state()


# ============================================================
# 手动实现DPO损失（高级用法）
# ============================================================

class DPOLoss(torch.nn.Module):
    """手动实现DPO损失"""
    
    def __init__(self, beta=0.1):
        super().__init__()
        self.beta = beta
        self.loss_fct = torch.nn.CrossEntropyLoss()
    
    def forward(self, policy_chosen_logps, policy_rejected_logps, 
                ref_chosen_logps, ref_rejected_logps):
        """
        计算DPO损失
        
        参数:
            policy_chosen_logps: 策略模型对chosen response的log概率
            policy_rejected_logps: 策略模型对rejected response的log概率
            ref_chosen_logps: 参考模型对chosen response的log概率
            ref_rejected_logps: 参考模型对rejected response的log概率
        """
        
        # 计算隐式奖励差异（带KL正则）
        chosen_logps = policy_chosen_logps - ref_chosen_logps
        rejected_logps = policy_rejected_logps - ref_rejected_logps
        
        # 计算log-sigmoid损失
        losses = -torch.nn.functional.logsigmoid(
            self.beta * (chosen_logps - rejected_logps)
        )
        
        return losses.mean()


def compute_log_probs(model, input_ids, attention_mask, labels):
    """
    计算序列的log概率
    
    返回:
        每个token的log概率之和
    """
    outputs = model(
        input_ids=input_ids,
        attention_mask=attention_mask,
        labels=labels
    )
    
    # 计算log概率
    log_probs = torch.nn.functional.log_softmax(outputs.logits, dim=-1)
    
    # 获取每个label位置的log概率
    label_log_probs = log_probs.gather(-1, labels.unsqueeze(-1)).squeeze(-1)
    
    # 只计算非padding部分的log概率
    mask = (labels != -100).float()
    per_token_logps = (label_log_probs * mask).sum(-1)
    
    return per_token_logps
