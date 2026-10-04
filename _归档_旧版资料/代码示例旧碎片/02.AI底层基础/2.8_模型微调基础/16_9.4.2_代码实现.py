"""
Prefix Tuning和P-Tuning v2实现
使用PEFT库
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PromptEncoderConfig, PromptEncoder, get_peft_model


# ============================================================
# Prefix Tuning实现
# ============================================================

def prefix_tuning_example():
    """Prefix Tuning示例"""
    
    # 加载模型
    model = AutoModelForCausalLM.from_pretrained(
        "gpt2",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Prefix Tuning配置
    prefix_config = PromptEncoderConfig(
        # 任务类型
        task_type="CAUSAL_LM",
        
        # Prompt编码器配置
        num_virtual_tokens=20,  # Prefix token数量
        
        # 编码器参数
        encoder_hidden_size=128,  # 中间层维度（可不同于模型维度）
        
        # 编码器层数
        encoder_num_layers=2,
        
        # 编码器dropout
        encoder_dropout=0.05,
    )
    
    # 应用Prefix Tuning
    model = get_peft_model(model, prefix_config, "prefix_tuning")
    
    # 查看参数
    model.print_trainable_parameters()
    
    # 训练
    # ... trainer.train() ...
    
    return model


# ============================================================
# P-Tuning v2实现
# ============================================================

def p_tuning_v2_example():
    """P-Tuning v2示例"""
    
    # P-Tuning v2本质上是Prefix Tuning + 逐层prefix
    # PEFT中通过设置不同的参数实现
    
    model = AutoModelForCausalLM.from_pretrained(
        "gpt2",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # P-Tuning v2配置
    # 关键区别：使用encoder_hidden_size等于模型维度
    p_tuning_config = PromptEncoderConfig(
        task_type="CAUSAL_LM",
        
        # P-Tuning v2通常需要更多的virtual tokens
        num_virtual_tokens=30,
        
        # P-Tuning v2：encoder维度等于模型维度
        encoder_hidden_size=768,  # 对于gpt2是768
        
        # P-Tuning v2可以有多层
        encoder_num_layers=3,
        
        encoder_dropout=0.05,
    )
    
    model = get_peft_model(model, p_tuning_config, "p_tuning_v2")
    model.print_trainable_parameters()
    
    return model


# ============================================================
# 手动实现P-Tuning v2（理解原理）
# ============================================================

class PTuningV2Config:
    """P-Tuning v2配置"""
    
    def __init__(self, num_layers, hidden_size, num_virtual_tokens):
        self.num_layers = num_layers
        self.hidden_size = hidden_size
        self.num_virtual_tokens = num_virtual_tokens


class VirtualTokensLayer(nn.Module):
    """P-Tuning v2的每一层prefix"""
    
    def __init__(self, num_virtual_tokens, hidden_size):
        super().__init__()
        # 可学习的虚拟token embedding
        self.embedding = nn.Embedding(num_virtual_tokens, hidden_size)
        
        # 可选的：每一层可以有独立的transform
        # self.ln = nn.LayerNorm(hidden_size)
    
    def forward(self, batch_size):
        """生成prefix"""
        # 返回 [batch_size, num_virtual_tokens, hidden_size]
        token_ids = torch.arange(
            self.num_virtual_tokens, 
            device=self.embedding.weight.device
        )
        tokens = self.embedding(token_ids)
        return tokens.unsqueeze(0).expand(batch_size, -1, -1)


class PrefixEncoder(nn.Module):
    """Prefix编码器，生成逐层的prefix向量"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        
        # 为每一层创建prefix
        self.prefix_layers = nn.ModuleList([
            VirtualTokensLayer(
                config.num_virtual_tokens,
                config.hidden_size
            )
            for _ in range(config.num_layers)
        ])
    
    def forward(self, batch_size):
        """返回所有层的prefix"""
        return [layer(batch_size) for layer in self.prefix_layers]


def inject_prefix_to_model(model, config):
    """
    将P-Tuning v2注入到模型中
    
    这是一个概念性实现
    实际需要根据具体模型架构修改
    """
    
    # 创建prefix编码器
    prefix_encoder = PrefixEncoder(config)
    
    # 原始模型的forward需要修改
    # 在每一层attention之前加上prefix
    
    def new_forward(input_ids, **kwargs):
        # 1. 原始embedding
        outputs = model.transformer.wte(input_ids)
        
        # 2. 获取prefix
        batch_size = input_ids.shape[0]
        prefix_list = prefix_encoder(batch_size)
        
        # 3. 逐层处理，在每层添加prefix
        for layer_idx, layer in enumerate(model.transformer.h):
            # 加上该层的prefix
            hidden_states = torch.cat([prefix_list[layer_idx], outputs], dim=1)
            
            # 原始layer处理
            outputs = layer(hidden_states)[0]
        
        # 后续处理...
        return outputs
    
    return model


# ============================================================
# 使用Transformers库的Trainer
# ============================================================

def use_with_trainer():
    """与Trainer配合使用"""
    
    from transformers import Trainer, TrainingArguments
    from peft import PromptEncoderConfig, get_peft_model
    
    model = AutoModelForCausalLM.from_pretrained("gpt2")
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    
    # PEFT配置
    peft_config = PromptEncoderConfig(
        task_type="CAUSAL_LM",
        num_virtual_tokens=20,
        encoder_hidden_size=128,
    )
    
    model = get_peft_model(model, peft_config)
    
    # 训练参数
    training_args = TrainingArguments(
        output_dir="./prefix_tuning_output",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        learning_rate=3e-4,  # Prefix Tuning通常使用较高学习率
        fp16=True,
    )
    
    # 创建Trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        tokenizer=tokenizer,
    )
    
    trainer.train()
    
    # 保存
    model.save_pretrained("./prefix_model")
