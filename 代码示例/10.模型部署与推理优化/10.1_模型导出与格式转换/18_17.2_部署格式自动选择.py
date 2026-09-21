class DeploymentFormatSelector:
    """根据部署环境自动选择最佳格式"""
    
    @staticmethod
    def detect_environment():
        """26. 检测部署环境"""
        import platform
        import torch
        
        environment = {
            "os": platform.system(),
            "python_version": platform.python_version(),
            "pytorch_version": torch.__version__,
            "has_cuda": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
            "has_gpu": torch.cuda.device_count() > 0 if torch.cuda.is_available() else False,
        }
        
        # 27. 检测可用的推理引擎
        available_engines = []
        
        if torch.cuda.is_available():
            available_engines.append("cuda")
            try:
                # 检查TensorRT
                import tensorrt
                available_engines.append("tensorrt")
            except ImportError:
                pass
        
        try:
            import onnxruntime
            available_engines.append("onnx_runtime")
        except ImportError:
            pass
        
        try:
            import onnx
            available_engines.append("onnx")
        except ImportError:
            pass
        
        environment["available_engines"] = available_engines
        
        return environment
    
    @staticmethod
    def select_format(environment, model_type="general"):
        """28. 根据环境和模型类型选择最佳格式
        
        参数:
            environment: 检测到的环境信息
            model_type: 模型类型（general/llm/vision等）
        
        返回:
            推荐使用的格式列表
        """
        recommendations = []
        
        # 29. GPU推理场景
        if environment.get("has_gpu"):
            if "tensorrt" in environment.get("available_engines", []):
                recommendations.append(("tensorrt", "NVIDIA GPU高性能推理"))
            if "onnx_runtime" in environment.get("available_engines", []):
                recommendations.append(("onnx_cuda", "ONNX Runtime CUDA加速"))
            recommendations.append(("torchscript", "PyTorch GPU推理"))
        
        # 30. CPU推理场景
        if "onnx_runtime" in environment.get("available_engines", []):
            recommendations.append(("onnx_cpu", "ONNX Runtime CPU推理"))
        
        if model_type == "llm":
            # 31. 大语言模型特殊处理
            if environment.get("os") == "Windows":
                recommendations.insert(0, ("gguf", "LLM CPU高效推理"))
            else:
                recommendations.insert(0, ("gguf", "LLM CPU/GPU推理"))
        
        # 32. 通用场景
        if not recommendations:
            recommendations.append(("pytorch", "PyTorch原生"))
            recommendations.append(("torchscript", "TorchScript优化"))
        
        return recommendations
    
    @staticmethod
    def get_format_for_deployment(deployment_type):
        """33. 根据部署类型获取推荐格式
        
        参数:
            deployment_type: 部署类型
                - "api_service": API服务
                - "batch_processing": 批处理
                - "realtime": 实时推理
                - "edge_device": 边缘设备
                - "mobile": 移动端
                - "browser": 浏览器
        """
        
        format_map = {
            "api_service": {
                "recommended": ["torchscript", "onnx"],
                "alternative": ["pytorch"],
                "description": "API服务通常使用TorchScript或ONNX"
            },
            "batch_processing": {
                "recommended": ["onnx", "torchscript"],
                "alternative": ["pytorch"],
                "description": "批处理追求吞吐量，格式影响不大"
            },
            "realtime": {
                "recommended": ["tensorrt", "onnx_cuda"],
                "alternative": ["torchscript"],
                "description": "实时推理需要低延迟，优先GPU加速"
            },
            "edge_device": {
                "recommended": ["torchscript", "onnx"],
                "alternative": [],
                "description": "边缘设备用TorchScript减少依赖"
            },
            "mobile": {
                "recommended": ["onnx", "coreml", "tflite"],
                "alternative": [],
                "description": "移动端使用平台特定格式"
            },
            "browser": {
                "recommended": ["onnx_js"],
                "alternative": [],
                "description": "浏览器使用ONNX.js"
            }
        }
        
        return format_map.get(deployment_type, {})

def demonstrate_deployment_selection():
    """34. 演示部署格式选择"""
    
    selector = DeploymentFormatSelector()
    
    # 35. 检测环境
    env = selector.detect_environment()
    
    print("=== 部署环境检测结果 ===")
    print(f"操作系统: {env['os']}")
    print(f"CUDA可用: {env['has_cuda']}")
    print(f"可用推理引擎: {env['available_engines']}")
    
    # 36. 获取格式推荐
    recommendations = selector.select_format(env, model_type="general")
    
    print("\n=== 推荐格式 ===")
    for format_name, reason in recommendations:
        print(f"  {format_name}: {reason}")
    
    # 37. 演示不同部署类型的格式选择
    print("\n=== 部署类型与格式对应 ===")
    for deploy_type in ["api_service", "realtime", "edge_device", "mobile"]:
        info = selector.get_format_for_deployment(deploy_type)
        print(f"\n{deploy_type}:")
        print(f"  推荐: {info.get('recommended', [])}")
        print(f"  说明: {info.get('description', '')}")

if __name__ == "__main__":
    # 测试导出功能
    # automated_export_pipeline()
    
    # 测试部署选择
    demonstrate_deployment_selection()
