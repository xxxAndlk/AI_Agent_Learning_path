"""
完整的模型量化示例

包含：
- PTQ动态量化
- PTQ静态量化
- QAT量化感知训练
- 精度对比
"""

import torch
import torch.nn as nn
import time
import os


class QuantizationDemo:
    """量化演示类"""
    
    def __init__(self):
        self.results = {}
    
    def create_sample_model(self) -> nn.Module:
        """创建示例模型"""
        model = nn.Sequential(
            nn.Linear(784, 512),
            nn.ReLU(),
            nn.Linear(512, 256),
            nn.ReLU(),
            nn.Linear(256, 10)
        )
        return model
    
    def get_model_size(self, model: nn.Module) -> float:
        """获取模型大小（MB）"""
        param_size = sum(p.numel() * p.element_size() for p in model.parameters())
        buffer_size = sum(b.numel() * b.element_size() for b in model.buffers())
        return (param_size + buffer_size) / (1024 * 1024)
    
    def test_inference_speed(
        self,
        model: nn.Module,
        input_data: torch.Tensor,
        num_runs: int = 100
    ) -> float:
        """测试推理速度"""
        model.eval()
        
        # 预热
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_data)
        
        # 计时
        start = time.time()
        with torch.no_grad():
            for _ in range(num_runs):
                _ = model(input_data)
        
        return (time.time() - start) / num_runs * 1000  # 毫秒
    
    def run_dynamic_quantization(self):
        """运行动态量化示例"""
        print("\n" + "="*60)
        print("1. 动态量化 (Dynamic Quantization)")
        print("="*60)
        
        # 创建模型
        model = self.create_sample_model()
        model.eval()
        
        # 原始模型信息
        original_size = self.get_model_size(model)
        print(f"原始模型大小: {original_size:.2f} MB")
        
        # 动态量化
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {nn.Linear},
            dtype=torch.qint8
        )
        
        # 量化后信息
        quantized_size = self.get_model_size(quantized_model)
        print(f"量化后大小: {quantized_size:.2f} MB")
        print(f"压缩比: {original_size / quantized_size:.2f}x")
        
        # 推理测试
        test_input = torch.randn(1, 784)
        original_time = self.test_inference_speed(model, test_input)
        quantized_time = self.test_inference_speed(quantized_model, test_input)
        
        print(f"\n推理时间对比:")
        print(f"  原始: {original_time:.2f} ms")
        print(f"  量化: {quantized_time:.2f} ms")
        print(f"  加速: {original_time / quantized_time:.2f}x")
        
        self.results['dynamic'] = {
            'size': quantized_size,
            'speedup': original_time / quantized_time
        }
    
    def run_static_quantization(self):
        """运行静态量化示例"""
        print("\n" + "="*60)
        print("2. 静态量化 (Static Quantization)")
        print("="*60)
        
        # 创建模型
        model = self.create_sample_model()
        
        # 准备量化
        model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
        torch.quantization.prepare(model, inplace=True)
        
        # 校准（使用随机数据模拟）
        print("校准中...")
        for _ in range(100):
            test_input = torch.randn(32, 784)
            model(test_input)
        
        # 转换为量化模型
        quantized_model = torch.quantization.convert(model)
        
        # 输出信息
        quantized_size = self.get_model_size(quantized_model)
        print(f"量化后大小: {quantized_size:.2f} MB")
        
        self.results['static'] = {
            'size': quantized_size
        }
    
    def run_all(self):
        """运行所有量化示例"""
        self.run_dynamic_quantization()
        self.run_static_quantization()
        
        print("\n" + "="*60)
        print("量化结果汇总")
        print("="*60)
        for method, result in self.results.items():
            print(f"{method}: {result}")


if __name__ == "__main__":
    demo = QuantizationDemo()
    demo.run_all()
