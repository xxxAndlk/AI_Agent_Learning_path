class InferenceContext:
    """AI模型推理上下文管理器"""
    
    def __init__(self, model, device: str = "cuda"):
        self.model = model
        self.device = device
    
    def __enter__(self):
        self.model.to(self.device)
        self.model.eval()                        # 切换到推理模式
        return self.model
    
    def __exit__(self, *args):
        # 清理GPU内存
        if self.device == "cuda":
            import torch
            torch.cuda.empty_cache()
        return False

# 使用
with InferenceContext(model, "cuda") as model:
    output = model(input_data)
