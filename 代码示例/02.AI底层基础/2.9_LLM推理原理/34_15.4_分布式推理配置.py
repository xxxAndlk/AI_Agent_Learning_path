"""
分布式推理完整配置
"""

# 1. 单机多卡配置
# 启动命令：
# python -m torch.distributed.launch \
#     --nproc_per_node=4 \
#     --master_port=29500 \
#     your_script.py

# 2. 多机多卡配置
# 节点0:
# python -m torch.distributed.launch \
#     --nnodes=2 \
#     --node_rank=0 \
#     --nproc_per_node=4 \
#     --master_addr=192.168.1.1 \
#     --master_port=29500 \
#     your_script.py

# 3. vLLM分布式服务
# 启动推理服务
"""
vllm serve meta-llama/Llama-2-70b-hf \
    --tensor-parallel-size 4 \
    --host 0.0.0.0 \
    --port 8000 \
    --trust-remote-code
"""

# 4. 使用Ray进行分布式部署
import ray
from ray import serve

@serve.deployment(num_replicas=2)
class LLMDeployment:
    def __init__(self):
        from vllm import LLM
        self.llm = LLM(
            model="meta-llama/Llama-2-7b-hf",
            tensor_parallel_size=1,
        )
    
    def generate(self, prompt: str):
        from vllm import SamplingParams
        outputs = self.llm.generate(
            [prompt],
            SamplingParams(max_tokens=100)
        )
        return outputs[0].outputs[0].text

# 部署
# serve.run(LLMDeployment.bind())

# 客户端调用
# handle = serve.get_deployment("LLMDeployment").get_handle()
# result = ray.get(handle.generate.remote("你好"))
