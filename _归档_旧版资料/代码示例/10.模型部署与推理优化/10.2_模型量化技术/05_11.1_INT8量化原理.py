class INT8Quantizer:
    """INT8量化器"""
    
    def __init__(self):
        self.scale = None
        self.zero_point = None
    
    def quantize_tensor(
        self,
        tensor: torch.Tensor,
        bit_width: int = 8
    ) -> tuple:
        """
        量化张量
        
        参数:
            tensor: 输入张量
            bit_width: 量化位数
        
        返回:
            (量化后的张量, 缩放因子, 零点)
        """
        # 计算统计信息
        min_val = tensor.min().item()
        max_val = tensor.max().item()
        
        # 对称量化
        if min_val == max_val:
            scale = 1.0
            zero_point = 0
        else:
            max_val = max(abs(min_val), abs(max_val))
            scale = max_val / (2 ** (bit_width - 1) - 1)
            zero_point = 0
        
        # 执行量化
        levels = 2 ** (bit_width - 1)
        quant_tensor = torch.clamp(
            torch.round(tensor / scale + zero_point),
            -levels,
            levels - 1
        ).to(torch.int8)
        
        self.scale = scale
        self.zero_point = zero_point
        
        return quant_tensor, scale, zero_point
    
    def dequantize_tensor(
        self,
        quant_tensor: torch.Tensor,
        scale: float,
        zero_point: int = 0
    ) -> torch.Tensor:
        """
        反量化张量
        
        参数:
            quant_tensor: 量化后的张量
            scale: 缩放因子
            zero_point: 零点
        
        返回:
            反量化后的张量
        """
        return quant_tensor.float() * scale
