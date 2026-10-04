class DynamicQuantization:
    """动态量化实现"""
    
    @staticmethod
    def quantize_model(model: nn.Module) -> nn.Module:
        """
        动态量化模型
        
        参数:
            model: 原始模型
        
        返回:
            量化后的模型
        """
        # torch.quantization.quantize_dynamic
        # 参数:
        #   - model: 要量化的模型
        #   - {nn.Linear, nn.LSTM}: 要量化的层类型
        #   - dtype: 量化数据类型
        quantized_model = torch.quantization.quantize_dynamic(
            model,
            {nn.Linear, nn.LSTM, nn.GRU},
            dtype=torch.qint8
        )
        
        return quantized_model


class StaticQuantization:
    """静态量化实现"""
    
    @staticmethod
    def quantize_model(
        model: nn.Module,
        calibration_data: List[torch.Tensor]
    ) -> nn.Module:
        """
        静态量化模型
        
        参数:
            model: 原始模型
            calibration_data: 校准数据
        
        返回:
            量化后的模型
        """
        # 1. 设置量化配置
        model.qconfig = torch.quantization.get_default_qconfig('fbgemm')
        
        # 2. 准备模型（插入观察器）
        torch.quantization.prepare(model, inplace=True)
        
        # 3. 校准（收集统计信息）
        model.eval()
        with torch.no_grad():
            for data in calibration_data:
                model(data)
        
        # 4. 转换为量化模型
        torch.quantization.convert(model, inplace=True)
        
        return model
