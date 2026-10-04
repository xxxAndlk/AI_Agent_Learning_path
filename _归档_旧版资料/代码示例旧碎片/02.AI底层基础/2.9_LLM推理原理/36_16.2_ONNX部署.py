import numpy as np

"""
ONNX模型导出与推理
"""

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
import onnxruntime as ort
from optimum.onnxruntime import ORTModelForCausalLM

# 方法1: 使用 optimum 导出
"""
# 安装: pip install optimum

optimum-cli export onnx \
    --model meta-llama/Llama-2-7b-chat-hf \
    --task text-generation \
    --quantization q8 \
    ./onnx_model/
"""

# 方法2: 手动导出
def export_to_onnx():
    """导出模型到ONNX格式"""
    
    model = AutoModelForCausalLM.from_pretrained(
        "meta-llama/Llama-2-7b-chat-hf",
        torch_dtype=torch.float16,
        device_map="cpu",
    )
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    
    # 创建虚拟输入
    dummy_input = tokenizer("测试", return_tensors="pt")
    input_ids = dummy_input["input_ids"]
    
    # 导出
    torch.onnx.export(
        model,
        (input_ids,),
        "llama.onnx",
        input_names=["input_ids"],
        output_names=["logits"],
        dynamic_axes={
            "input_ids": {0: "batch_size", 1: "sequence"},
            "logits": {0: "batch_size", 1: "sequence"},
        },
        opset_version=17,
    )
    print("模型已导出到 llama.onnx")

# ONNX推理
def infer_with_onnx():
    """使用ONNX Runtime推理"""
    
    # 创建推理会话
    sess_options = ort.SessionOptions()
    sess_options.graph_optimization_level = (
        ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    )
    
    session = ort.InferenceSession(
        "llama.onnx",
        sess_options,
        providers=["CPUExecutionProvider"],
    )
    
    tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    
    # 准备输入
    prompt = "你好，请介绍一下自己："
    inputs = tokenizer(prompt, return_tensors="np")
    input_ids = inputs["input_ids"].astype(np.int64)
    
    # 推理
    logits = session.run(None, {"input_ids": input_ids})[0]
    
    # 解码
    next_token = np.argmax(logits[0, -1, :])
    output = tokenizer.decode([next_token])
    
    print(f"输出: {output}")
