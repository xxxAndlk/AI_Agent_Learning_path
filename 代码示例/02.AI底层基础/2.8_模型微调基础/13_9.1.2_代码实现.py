"""
RLHF训练实现
使用TRL库进行PPO训练
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTTrainer, DPOTrainer, PPOTrainer
from trl.core import LengthSampler
from peft import LoraConfig

# ============================================================
# 阶段1：监督微调 (SFT)
# ============================================================

def sft_training_example():
    """SFT监督微调示例"""
    
    # 加载模型和tokenizer
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-hf")
    
    # 配置LoRA（推荐使用PEFT）
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
        lora_dropout=0.05,
        task_type="CAUSAL_LM"
    )
    
    # SFT训练器配置
    sft_trainer = SFTTrainer(
        model=model,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        peft_config=lora_config,
        tokenizer=tokenizer,
        max_seq_length=512,
        formatting_func=formatting_prompts_func,
        
        # 训练参数
        num_train_epochs=3,
        per_device_train_batch_size=4,
        gradient_accumulation_steps=4,
        learning_rate=2e-4,
        weight_decay=0.01,
        warmup_ratio=0.1,
        
        # 日志和保存
        logging_steps=10,
        save_steps=500,
        save_total_limit=2,
        
        # 优化配置
        fp16=True,
        remove_unused_columns=False,
    )
    
    sft_trainer.train()
    sft_trainer.save_model("./sft_model")


# ============================================================
# 阶段2：奖励模型训练
# ============================================================

def reward_model_training_example():
    """奖励模型训练示例"""
    
    from trl import RewardTrainer
    from transformers import AutoModelForSequenceClassification
    
    # 加载基础模型作为奖励模型
    # 奖励模型是一个分类器，输出标量奖励值
    reward_model = AutoModelForSequenceClassification.from_pretrained(
        "meta-llama/Llama-2-7b-hf",
        num_labels=1,  # 输出单个奖励分数
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 奖励模型训练器
    reward_trainer = RewardTrainer(
        model=reward_model,
        train_dataset=reward_dataset,  # 偏好数据
        eval_dataset=reward_eval_dataset,
        tokenizer=tokenizer,
        max_length=512,
        
        # 训练参数
        num_train_epochs=3,
        per_device_train_batch_size=8,
        learning_rate=1e-5,
        weight_decay=0.01,
        
        # 评估指标
        eval_metrics=["accuracy"],
    )
    
    reward_trainer.train()
    reward_trainer.save_model("./reward_model")


# ============================================================
# 阶段3：PPO强化学习
# ============================================================

def ppo_training_example():
    """PPO强化学习训练示例"""
    
    from trl import PPOConfig
    
    # 加载SFT模型（作为策略模型）
    model = AutoModelForCausalLM.from_pretrained(
        "./sft_model",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # 加载奖励模型
    reward_model = AutoModelForSequenceClassification.from_pretrained(
        "./reward_model",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # PPO配置
    ppo_config = PPOConfig(
        # 训练参数
        num_ppo_epochs=4,
        batch_size=256,
        mini_batch_size=4,
        gradient_accumulation_steps=1,
        
        # 学习率
        learning_rate=1e-5,
        lr_scheduler_type="cosine",
        
        # PPO特定参数
        gamma=1.0,
        lam=0.95,
        cliprange=0.2,
        cliprange_value=0.2,
        vf_coef=0.1,
        ent_coef=0.01,
        
        # KL惩罚
        kl_control=0.1,  # KL散度系数
        
        # 生成参数
        max_response_length=512,
        max_prompt_length=256,
    )
    
    # 创建PPO训练器
    ppo_trainer = PPOTrainer(
        config=ppo_config,
        model=model,
        reward_model=reward_model,
        tokenizer=tokenizer,
        dataset=dataset,
        data_collator=data_collator,
    )
    
    # 生成器配置
    generation_kwargs = {
        "max_length": 512,
        "temperature": 0.7,
        "top_p": 0.9,
        "do_sample": True,
    }
    
    # PPO训练循环
    for epoch in range(ppo_config.num_train_epochs):
        for batch in ppo_trainer.dataloader:
            # 1. 使用当前策略生成response
            query_tensors = batch["input_ids"]
            response_tensors = ppo_trainer.generate(
                query_tensors,
                return_prompt=False,
                **generation_kwargs
            )
            
            # 2. 计算奖励
            batch["response"] = tokenizer.batch_decode(response_tensors)
            rewards = []
            for query, response in zip(batch["query"], batch["response"]):
                reward = compute_reward(query, response)  # 自定义奖励函数
                rewards.append(torch.tensor(reward))
            
            # 3. PPO训练步骤
            stats = ppo_trainer.step(query_tensors, response_tensors, rewards)
            
            # 4. 记录日志
            if epoch % 10 == 0:
                print(f"Epoch {epoch}: {stats}")
    
    # 保存最终模型
    model.save_pretrained("./rlhf_model")


# 辅助函数
def compute_reward(query, response):
    """
    自定义奖励计算函数
    可以结合多个信号：RM分数、长度惩罚、格式惩罚等
    """
    # 这里可以使用奖励模型或自定义逻辑
    return reward_score  # 返回标量
