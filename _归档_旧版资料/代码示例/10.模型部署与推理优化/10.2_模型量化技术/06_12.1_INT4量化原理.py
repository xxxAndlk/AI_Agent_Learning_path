class INT4Quantizer:
    """INT4量化器"""
    
    def __init__(self):
        self.scales = {}
        self.group_size = 128  # 按组量化
    
    def quantize_tensor_group(
        self,
        tensor: torch.Tensor,
        group_size: int = 128
    ) -> tuple:
        """
        按组量化张量
        
        参数:
            tensor: 输入张量
            group_size: 每组的元素数量
        
        返回:
            (量化张量, 缩放因子列表, 形状信息)
        """
        # 获取原始形状
        original_shape = tensor.shape
        
        # 展平以便分组
        flat_tensor = tensor.flatten()
        
        # 填充到组大小的倍数
        remainder = flat_tensor.numel() % group_size
        if remainder != 0:
            padding = group_size - remainder
            flat_tensor = torch.cat([
                flat_tensor,
                torch.zeros(padding, dtype=flat_tensor.dtype)
            ])
        
        # 重塑为组
        num_groups = flat_tensor.numel() // group_size
        grouped_tensor = flat_tensor.view(num_groups, group_size)
        
        # 计算每组的缩放因子
        scales = grouped_tensor.abs().max(dim=1).values
        scales = scales / 7.0  # INT4范围[-7, 7]
        
        # 量化
        quant_tensor = torch.clamp(
            torch.round(grouped_tensor / scales.unsqueeze(1)),
            -7, 7
        ).to(torch.int8)
        
        self.scales['default'] = scales
        
        return quant_tensor, scales, original_shape
    
    def dequantize_tensor_group(
        self,
        quant_tensor: torch.Tensor,
        scales: torch.Tensor,
        original_shape: tuple
    ) -> torch.Tensor:
        """
        按组反量化
        
        参数:
            quant_tensor: 量化张量
            scales: 缩放因子
            original_shape: 原始形状
        
        返回:
            恢复的张量
        """
        # 反量化
        dequant = quant_tensor.float() * scales.unsqueeze(1)
        
        # 恢复形状
        flat_result = dequant.flatten()[:torch.tensor(original_shape).numel()]
        
        return flat_result.view(original_shape)
