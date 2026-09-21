import torch
import torch.nn as nn
import numpy as np

class PTQQuantizer:
    """训练后量化器"""
    
    def __init__(self, model: nn.Module):
        """
        初始化量化器
        
        参数:
            model: 待量化的PyTorch模型
        """
        self.model = model
        self.original_state_dict = None
        self.quantization_params = {}
    
    def collect_statistics(self, calibration_data: torch.Tensor):
        """
        收集校准数据统计信息
        
        参数:
            calibration_data: 校准数据
        """
        self.model.eval()
        
        # 遍历所有Linear层
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                # 收集权重统计信息
                weight = module.weight.data
                
                # 计算最小值和最大值
                w_min = weight.min().item()
                w_max = weight.max().item()
                
                # 对称量化范围
                abs_max = max(abs(w_min), abs(w_max))
                
                self.quantization_params[name] = {
                    'min': w_min,
                    'max': w_max,
                    'abs_max': abs_max,
                    'scale': abs_max / 127.0,  # INT8范围
                    'zero_point': 0
                }
    
    def quantize(self, bit_width: int = 8) -> nn.Module:
        """
        执行量化
        
        参数:
            bit_width: 量化位数（8或4）
        
        返回:
            量化后的模型
        """
        # 保存原始权重
        self.original_state_dict = {
            name: param.clone()
            for name, param in self.model.state_dict().items()
        }
        
        # 计算量化范围
        num_levels = 2 ** bit_width - 1
        
        for name, module in self.model.named_modules():
            if isinstance(module, nn.Linear):
                weight = module.weight.data
                
                # 计算缩放因子
                abs_max = weight.abs().max().item()
                scale = abs_max / (num_levels / 2)
                
                # 量化到INT8
                weight_quant = torch.clamp(
                    torch.round(weight / scale),
                    -num_levels // 2,
                    num_levels // 2 - 1
                )
                
                # 反量化回FP32
                weight_dequant = weight_quant * scale
                
                # 更新权重
                module.weight.data = weight_dequant
        
        return self.model
    
    def get_model_size(self, model: nn.Module) -> float:
        """
        计算模型大小
        
        参数:
            model: 模型
        
        返回:
            模型大小（MB）
        """
        param_size = 0
        for param in model.parameters():
            param_size += param.nelement() * param.element_size()
        
        buffer_size = 0
        for buffer in model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()
        
        size_mb = (param_size + buffer_size) / (1024 * 1024)
        return size_mb
    
    def restore_original(self):
        """恢复原始权重"""
        if self.original_state_dict:
            self.model.load_state_dict(self.original_state_dict)
