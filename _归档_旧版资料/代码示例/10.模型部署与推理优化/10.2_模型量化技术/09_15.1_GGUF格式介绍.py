class GGUFQuantizer:
    """GGUF格式量化器"""
    
    # GGUF量化类型定义
    QUANT_TYPES = {
        'Q4_0': {'bits': 4, 'block_size': 32, 'description': '4位，经典格式'},
        'Q4_1': {'bits': 4, 'block_size': 32, 'description': '4位，带缩放因子'},
        'Q5_0': {'bits': 5, 'block_size': 32, 'description': '5位，经典格式'},
        'Q5_1': {'bits': 5, 'block_size': 32, 'description': '5位，带缩放因子'},
        'Q8_0': {'bits': 8, 'block_size': 32, 'description': '8位，接近INT8'}
    }
    
    def __init__(self, quant_type: str = 'Q4_0'):
        """
        初始化GGUF量化器
        
        参数:
            quant_type: 量化类型
        """
        self.quant_type = quant_type
        self.config = self.QUANT_TYPES.get(quant_type, self.QUANT_TYPES['Q4_0'])
    
    def quantize_tensor(
        self,
        tensor: torch.Tensor
    ) -> tuple:
        """
        GGUF格式量化
        
        参数:
            tensor: 输入张量
        
        返回:
            (量化数据, 元数据)
        """
        bits = self.config['bits']
        block_size = self.config['block_size']
        
        # 展平并分组
        flat = tensor.flatten()
        n_blocks = (flat.numel() + block_size - 1) // block_size
        
        # 初始化输出
        quant_data = []
        scales = []
        
        for i in range(n_blocks):
            # 获取当前块
            start = i * block_size
            end = min(start + block_size, flat.numel())
            block = flat[start:end]
            
            # 计算块缩放因子
            max_val = block.abs().max()
            scale = max_val / (2 ** (bits - 1) - 1) if max_val > 0 else 1.0
            
            # 量化
            block_quant = torch.clamp(
                torch.round(block / scale),
                -(2 ** (bits - 1)),
                2 ** (bits - 1) - 1
            ).to(torch.int8)
            
            quant_data.append(block_quant)
            scales.append(scale)
        
        return torch.stack(quant_data), torch.tensor(scales)
