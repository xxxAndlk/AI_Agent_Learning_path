def parse_model_config(config: dict):
    """解析模型配置"""
    match config:
        case {"type": "resnet", "layers": n}:
            return f"ResNet-{n}"
        
        case {"type": "transformer", "heads": h, "depth": d}:
            return f"Transformer-{h}heads-{d}depth"
        
        case {"type": "cnn", "filters": f} if f >= 32:
            return f"CNN-{f}filters"
        
        case _:
            return "未知模型类型"
