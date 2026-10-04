"""
张量并行推理实现
使用vLLM进行张量并行
"""

from vllm import LLM, SamplingParams

# 4卡张量并行
llm = LLM(
    model="meta-llama/Llama-2-70b-hf",
    tensor_parallel_size=4,              # 使用4张GPU
    gpu_memory_utilization=0.9,
    trust_remote_code=True,
)

# 生成
sampling_params = SamplingParams(
    max_tokens=200,
    temperature=0.7,
)

output = llm.generate(
    ["写一个关于深度学习的教程："],
    sampling_params
)

print(output[0].outputs[0].text)

# 使用Transformers进行手动张量并行
import torch
import torch.distributed as dist
from transformers import AutoModelForCausalLM, AutoConfig

class TensorParallelModel:
    """手动张量并行实现"""
    
    def __init__(self, model_name: str, tensor_parallel_size: int = 2):
        self.tp_size = tensor_parallel_size
        
        # 获取本地排名
        self.rank = dist.get_rank()
        self.world_size = dist.get_world_size()
        
        # 加载配置并修改
        config = AutoConfig.from_pretrained(model_name)
        config.tensor_parallel_size = self.tp_size
        config.rank = self.rank
        
        # 只加载本地部分
        self.model = AutoModelForCausalLM.from_config(
            config,
            torch_dtype=torch.float16,
        )
        
        # 设置设备
        self.device = torch.device(f"cuda:{self.rank}")
        self.model = self.model.to(self.device)
    
    def forward(self, input_ids: torch.Tensor):
        """分布式前向传播"""
        
        # 收集输入到所有设备
        dist.broadcast(input_ids, src=0)
        
        # 本地计算
        outputs = self.model(input_ids)
        
        # 聚合logits（张量并行最后一步）
        # 假设最后一层是ColumnParallelLinear
        if self.tp_size > 1:
            logits = outputs.logits
            # All-reduce
            dist.all_reduce(logits, op=dist.ReduceOp.SUM)
        
        return outputs
