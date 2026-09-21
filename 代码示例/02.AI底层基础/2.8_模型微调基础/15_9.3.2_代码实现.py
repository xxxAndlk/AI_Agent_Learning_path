"""
Adapter实现
使用HuggingFace Adapter库
"""

import torch
import torch.nn as nn
from transformers import AdapterConfig, AdapterType
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import AdapterConfig, get_peft_model


# ============================================================
# 使用PEFT库实现Adapter
# ============================================================

def adapter_with_peft_example():
    """使用PEFT库实现Adapter"""
    
    # 加载基础模型
    model = AutoModelForCausalLM.from_pretrained(
        "gpt2",
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    # Adapter配置
    adapter_config = AdapterConfig(
        # 瓶颈维度
        bottleneck_size=64,  # r
        
        # 非线性激活
        nonlinearity="relu",  # 或 "gelu"
        
        # 残差连接
        residual_before_ln=True,
        
        # 串行/并行
        parallel_adapter=False,
        
        # 缩放
        scaling=1.0,
        
        # dropout
        dropout=0.05,
    )
    
    # 应用Adapter
    model = get_peft_model(
        model,
        adapter_config,
        adapter_name="task_adapter"
    )
    
    # 查看可训练参数
    model.print_trainable_parameters()
    # 输出类似：trainable params: 1,234,567 || all params: 124,567,890 || trainable%: 0.99%
    
    # 训练配置
    training_args = {
        "num_train_epochs": 3,
        "per_device_train_batch_size": 4,
        "learning_rate": 1e-4,  # Adapter通常使用较高学习率
        "fp16": True,
    }
    
    return model


# ============================================================
# 手动实现Adapter层
# ============================================================

class AdapterLayer(nn.Module):
    """手动实现Adapter层"""
    
    def __init__(self, hidden_size, bottleneck_size=64, dropout=0.05):
        super().__init__()
        self.hidden_size = hidden_size
        self.bottleneck_size = bottleneck_size
        
        # 下投影：d → r
        self.down_project = nn.Linear(hidden_size, bottleneck_size)
        
        # 上投影：r → d
        self.up_project = nn.Linear(bottleneck_size, hidden_size)
        
        # 激活函数
        self.activation = nn.ReLU()
        
        # Dropout
        self.dropout = nn.Dropout(dropout)
        
        # LayerNorm（可选，用于稳定训练）
        # self.layer_norm = nn.LayerNorm(hidden_size)
    
    def forward(self, x):
        """
        Adapter前向传播
        
        参数:
            x: [batch, seq_len, hidden_size]
        返回:
            加上adapter增量后的输出
        """
        # 残差连接：output = x + adapter(x)
        residual = x
        
        # Down projection
        h = self.down_project(x)
        h = self.activation(h)
        h = self.dropout(h)
        
        # Up projection
        h = self.up_project(h)
        
        # Dropout（推理时不生效）
        h = self.dropout(h)
        
        # 残差连接
        output = residual + h
        
        return output


def insert_adapters_to_model(model, bottleneck_size=64, dropout=0.05):
    """
    将Adapter插入到预训练模型的每一层
    
    这个函数展示了如何修改模型结构
    实际使用中推荐使用AdapterHub库
    """
    
    # 遍历模型的所有模块
    for name, module in model.named_modules():
        # 找到FFN层（在Attention之后的Feed-Forward层）
        if isinstance(module, nn.Linear) and "mlp" in name.lower():
            # 在FFN后添加Adapter
            adapter = AdapterLayer(
                hidden_size=module.out_features,
                bottleneck_size=bottleneck_size,
                dropout=dropout
            )
            
            # 获取父模块
            parent_name = ".".join(name.split(".")[:-1])
            parent = model.get_submodule(parent_name)
            
            # 替换或添加
            # 实际实现需要更复杂的逻辑
            pass
    
    return model


# ============================================================
# 使用AdapterHub库（更完整方案）
# ============================================================

def adapterhub_example():
    """使用AdapterHub库的完整示例"""
    
    # 注意：需要安装 adapter-transformers 库
    # pip install adapter-transformers
    
    from adapter_transformers import AdapterModel, AdapterConfig
    
    # 加载模型
    model = AdapterModel.from_pretrained(
        "bert-base-uncased",
        adapter_config=AdapterConfig(
            # Adapter类型
            adapter_type="seq",  # "seq" or "par"
            
            # 瓶颈维度
            md_dim=64,
            
            # 隐藏层维度
            d_model=768,
            
            # 注意力相关
            add_adapter_before_ln=True,
            
            # 任务相关参数
            task_specific_params={"language": "en"},
        )
    )
    
    # 添加Adapter
    model.add_adapter("sentiment_adapter", config="pfeiffer")
    
    # 设置Adapter为激活状态
    model.set_active_adapters("sentiment_adapter")
    
    # 冻结原始参数
    for name, param in model.named_parameters():
        if "adapter" not in name:
            param.requires_grad = False
    
    # 训练Adapter
    # ... 训练代码 ...
    
    # 保存Adapter
    model.save_adapter("./adapters/sentiment", "sentiment_adapter")
    
    # 加载Adapter
    model.load_adapter("./adapters/sentiment")
    model.set_active_adapters("sentiment_adapter")
