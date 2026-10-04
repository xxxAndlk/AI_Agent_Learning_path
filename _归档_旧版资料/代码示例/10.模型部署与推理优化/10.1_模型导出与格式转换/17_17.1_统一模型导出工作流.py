import os                          # 1. 导入必要的库
import json
from pathlib import Path
from datetime import datetime

class MultiFormatExporter:
    """多格式模型导出管理器
    
    自动化处理模型导出到多种格式的流程
    """
    
    def __init__(self, model, model_name="model", output_dir="./exports"):
        """2. 初始化导出器
        
        参数:
            model: 要导出的PyTorch模型
            model_name: 模型名称，用于文件命名
            output_dir: 输出目录
        """
        self.model = model
        self.model_name = model_name
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. 导出元数据记录
        self.export_info = {
            "model_name": model_name,
            "export_date": datetime.now().isoformat(),
            "pytorch_version": None,  # 将在导出时填充
            "formats": {}
        }
    
    def export_all_formats(self, example_input, onnx_opset=13):
        """4. 导出为所有支持的格式
        
        参数:
            example_input: 示例输入张量
            onnx_opset: ONNX算子集版本
        """
        import torch
        
        # 5. 记录PyTorch版本
        self.export_info["pytorch_version"] = torch.__version__
        
        # 6. 导出PyTorch原始格式
        self._export_pytorch()
        
        # 7. 导出TorchScript
        self._export_torchscript(example_input)
        
        # 8. 导出ONNX
        self._export_onnx(example_input, onnx_opset)
        
        # 9. 导出Safetensors
        self._export_safetensors()
        
        # 10. 保存导出元数据
        self._save_metadata()
        
        print(f"\n✅ 所有格式导出完成！")
        print(f"📁 输出目录: {self.output_dir}")
        
        return self.export_info
    
    def _export_pytorch(self):
        """11. 导出PyTorch格式"""
        import torch
        
        # 12. 准备模型（评估模式）
        self.model.eval()
        
        # 13. 保存state_dict（推荐方式）
        save_path = self.output_dir / f"{self.model_name}.pth"
        torch.save(self.model.state_dict(), save_path)
        
        self.export_info["formats"]["pytorch"] = {
            "file": str(save_path.name),
            "method": "state_dict"
        }
        print(f"✅ PyTorch格式: {save_path}")
    
    def _export_torchscript(self, example_input):
        """14. 导出TorchScript格式"""
        import torch
        
        # 15. 使用Tracing方式
        try:
            traced = torch.jit.trace(self.model, example_input)
            
            # 16. 进一步优化
            optimized = torch.jit.optimize_for_inference(traced)
            
            save_path = self.output_dir / f"{self.model_name}_torchscript.pt"
            optimized.save(str(save_path))
            
            self.export_info["formats"]["torchscript"] = {
                "file": str(save_path.name),
                "method": "tracing + optimization"
            }
            print(f"✅ TorchScript格式: {save_path}")
        except Exception as e:
            print(f"⚠️ TorchScript导出失败: {e}")
    
    def _export_onnx(self, example_input, opset_version):
        """17. 导出ONNX格式"""
        import torch
        
        try:
            # 18. 导出ONNX
            save_path = self.output_dir / f"{self.model_name}.onnx"
            
            torch.onnx.export(
                self.model,
                example_input,
                str(save_path),
                export_params=True,
                opset_version=opset_version,
                do_constant_folding=True,
                input_names=['input'],
                output_names=['output'],
                dynamic_axes={
                    'input': {0: 'batch_size'},
                    'output': {0: 'batch_size'}
                }
            )
            
            self.export_info["formats"]["onnx"] = {
                "file": str(save_path.name),
                "opset_version": opset_version
            }
            print(f"✅ ONNX格式: {save_path}")
        except Exception as e:
            print(f"⚠️ ONNX导出失败: {e}")
    
    def _export_safetensors(self):
        """19. 导出Safetensors格式"""
        try:
            import safetensors.torch
            
            save_path = self.output_dir / f"{self.model_name}.safetensors"
            
            state_dict = self.model.state_dict()
            safetensors.torch.save_file(state_dict, str(save_path))
            
            self.export_info["formats"]["safetensors"] = {
                "file": str(save_path.name),
                "method": "safe_serialization"
            }
            print(f"✅ Safetensors格式: {save_path}")
        except ImportError:
            print("⚠️ Safetensors库未安装，跳过")
    
    def _save_metadata(self):
        """20. 保存导出元数据"""
        metadata_path = self.output_dir / f"{self.model_name}_metadata.json"
        
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(self.export_info, f, ensure_ascii=False, indent=2)
        
        print(f"📄 元数据: {metadata_path}")

def automated_export_pipeline():
    """21. 自动化导出流程示例"""
    
    print("=== 自动化模型导出流程 ===\n")
    
    # 22. 创建示例模型
    class DemoModel:
        pass
    
    # 23. 模型定义（简化版）
    model = torch.nn.Sequential(
        torch.nn.Conv2d(3, 32, 3, padding=1),
        torch.nn.ReLU(),
        torch.nn.MaxPool2d(2),
        torch.nn.Conv2d(32, 64, 3, padding=1),
        torch.nn.ReLU(),
        torch.nn.AdaptiveAvgPool2d((1, 1)),
        torch.nn.Flatten(),
        torch.nn.Linear(64, 10)
    )
    
    # 24. 准备示例输入
    example_input = torch.randn(1, 3, 32, 32)
    
    # 25. 导出所有格式
    exporter = MultiFormatExporter(model, "demo_model", "./exports")
    exporter.export_all_formats(example_input)
