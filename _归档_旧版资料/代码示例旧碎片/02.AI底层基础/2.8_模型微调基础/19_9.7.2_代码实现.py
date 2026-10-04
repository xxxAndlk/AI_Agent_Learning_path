"""
灾难性遗忘缓解策略实现
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import LoraConfig, get_peft_model
from copy import deepcopy


# ============================================================
# 方法1：EWC（弹性权重固结）
# ============================================================

class EWC:
    """
    弹性权重固结 (Elastic Weight Consolidation)
    
    原理：在损失函数中添加参数重要性的正则项
    L = L_task + λ * Σ F_i * (θ_i - θ*_i)²
    
    其中F_i是费舍尔信息矩阵（Fisher Information）
    """
    
    def __init__(self, model, dataloader, device):
        self.model = model
        self.device = device
        
        # 存储原始参数
        self.params = {n: p.clone() for n, p in model.named_parameters() if p.requires_grad}
        
        # 计算费舍尔信息矩阵
        self.fisher_info = self.compute_fisher(dataloader)
    
    def compute_fisher(self, dataloader):
        """计算费舍尔信息矩阵"""
        fisher = {}
        
        # 初始化Fisher为0
        for n, p in self.model.named_parameters():
            if p.requires_grad:
                fisher[n] = torch.zeros_like(p.data)
        
        # 收集梯度信息
        self.model.eval()
        for batch in dataloader:
            # 前向传播
            inputs = {k: v.to(self.device) for k, v in batch.items()}
            outputs = self.model(**inputs)
            loss = outputs.loss
            
            # 反向传播
            self.model.zero_grad()
            loss.backward()
            
            # 收集梯度
            for n, p in self.model.named_parameters():
                if p.requires_grad and p.grad is not None:
                    fisher[n] += p.grad.data.clone() ** 2
        
        # 平均
        num_samples = len(dataloader)
        for n in fisher:
            fisher[n] /= num_samples
        
        return fisher
    
    def penalty(self):
        """计算EWC惩罚项"""
        loss = 0
        for n, p in self.model.named_parameters():
            if n in self.fisher_info:
                loss += (self.fisher_info[n] * (p - self.params[n]) ** 2).sum()
        return loss


def ewc_training_example():
    """使用EWC进行训练"""
    
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-4)
    ewc = EWC(model, original_dataloader, device)
    
    lambda_ewc = 5000  # EWC强度
    
    for batch in new_task_dataloader:
        optimizer.zero_grad()
        
        # 新任务损失
        outputs = model(**batch)
        task_loss = outputs.loss
        
        # EWC正则化损失
        ewc_loss = lambda_ewc * ewc.penalty()
        
        # 总损失
        loss = task_loss + ewc_loss
        
        loss.backward()
        optimizer.step()


# ============================================================
# 方法2：经验回放
# ============================================================

def 经验回放示例():
    """经验回放（Experience Replay）"""
    
    # 方案1：数据混合
    def mix_datasets(domain_data, general_data, mix_ratio=0.5):
        """
        混合领域数据和通用数据
        
        参数:
            domain_data: 领域数据
            general_data: 通用/原始数据
            mix_ratio: 领域数据比例
        """
        import random
        random.shuffle(general_data)
        
        # 按比例混合
        num_domain = int(len(general_data) * mix_ratio / (1 - mix_ratio))
        mixed_data = domain_data[:num_domain] + general_data
        
        random.shuffle(mixed_data)
        return mixed_data
    
    # 方案2：动态回放缓冲区
    class ReplayBuffer:
        def __init__(self, capacity=1000):
            self.buffer = []
            self.capacity = capacity
        
        def add(self, sample):
            self.buffer.append(sample)
            if len(self.buffer) > self.capacity:
                self.buffer.pop(0)
        
        def sample(self, batch_size):
            import random
            return random.sample(self.buffer, min(batch_size, len(self.buffer)))
    
    # 方案3：重要性采样回放
    def importance_replay(model, domain_data, replay_buffer, beta=0.5):
        """
        基于重要性的回放
        对预测不确定性高的样本增加采样概率
        """
        model.eval()
        importances = []
        
        for sample in domain_data:
            with torch.no_grad():
                outputs = model(**sample)
                # 使用loss作为不确定性指标
                uncertainty = outputs.loss.item()
                importances.append(uncertainty)
        
        # 归一化
        importances = torch.tensor(importances)
        probs = importances / importances.sum()
        
        # 采样
        indices = torch.multinomial(probs, len(domain_data), replacement=True)
        replayed_data = [domain_data[i] for i in indices]
        
        return replayed_data


# ============================================================
# 方法3：LoRA（天然缓解）
# ============================================================

def lora_mitigates_forgetting():
    """LoRA天然缓解灾难性遗忘"""
    
    # LoRA只更新低秩矩阵
    # 原始权重保持冻结
    
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    
    # 只训练LoRA参数
    lora_config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["q_proj", "v_proj"],
    )
    
    model = get_peft_model(model, lora_config)
    
    # 原始权重保持不变
    # 灾难性遗忘自然缓解
    # 但无法完全避免（attention输出还是变了）
    
    return model


# ============================================================
# 方法4：知识蒸馏
# ============================================================

class DistillationLoss(nn.Module):
    """知识蒸馏损失"""
    
    def __init__(self, temperature=2.0, alpha=0.5):
        super().__init__()
        self.temperature = temperature
        self.alpha = alpha
    
    def forward(self, student_logits, teacher_logits, labels):
        """
        计算蒸馏损失
        
        参数:
            student_logits: 学生模型输出
            teacher_logits: 教师模型（原始模型）输出
            labels: 真实标签
        """
        # 软目标损失（KL散度）
        soft_student = F.log_softmax(student_logits / self.temperature, dim=-1)
        soft_teacher = F.softmax(teacher_logits / self.temperature, dim=-1)
        distillation_loss = F.kl_div(
            soft_student, soft_teacher, reduction='batchmean'
        ) * (self.temperature ** 2)
        
        # 硬目标损失（交叉熵）
        hard_loss = F.cross_entropy(student_logits, labels)
        
        # 加权组合
        loss = self.alpha * distillation_loss + (1 - self.alpha) * hard_loss
        
        return loss


def distillation_training():
    """使用知识蒸馏训练"""
    
    # 加载学生模型（微调后）
    student_model = AutoModelForCausalLM.from_pretrained("./finetuned_model")
    
    # 加载教师模型（原始预训练模型）
    teacher_model = AutoModelForCausalLM.from_pretrained("gpt2")
    teacher_model.eval()
    
    # 冻结教师模型
    for param in teacher_model.parameters():
        param.requires_grad = False
    
    # 蒸馏损失
    distillation_loss_fn = DistillationLoss(temperature=2.0, alpha=0.7)
    
    # 训练循环
    for batch in dataloader:
        # 教师输出（不计算梯度）
        with torch.no_grad():
            teacher_outputs = teacher_model(**batch)
        
        # 学生输出
        student_outputs = student_model(**batch)
        
        # 计算蒸馏损失
        loss = distillation_loss_fn(
            student_outputs.logits,
            teacher_outputs.logits,
            batch["labels"]
        )
        
        loss.backward()
        optimizer.step()


# ============================================================
# 方法5：渐进式微调
# ============================================================

def progressive_finetuning():
    """渐进式微调：从简单到复杂"""
    
    # 策略：先微调浅层，逐步解冻更深层
    
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    
    # 阶段1：只训练最后一层
    for name, param in model.named_parameters():
        if "lm_head" not in name:
            param.requires_grad = False
    
    # 训练阶段1...
    
    # 阶段2：解冻最后N层
    # 解冻更多层...
    
    # 阶段3：可选全量微调（使用较小学习率）
    for param in model.parameters():
        param.requires_grad = True
    
    # 使用较小学习率进行全量微调
    optimizer = torch.optim.AdamW(model.parameters(), lr=1e-5)
