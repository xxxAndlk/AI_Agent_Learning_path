class AWQQuantizer:
    """AWQ量化器"""
    
    def __init__(
        self,
        model: nn.Module,
        bit_width: int = 4
    ):
        """
        初始化AWQ量化器
        
        参数:
            model: 待量化模型
            bit_width: 量化位数
        """
        self.model = model
        self.bit_width = bit_width
        self.activation_scales = {}
    
    def compute_activation_scales(
        self,
        calibration_data: torch.Tensor
    ):
        """
        计算激活值缩放
        
        参数:
            calibration_data: 校准数据
        """
        self.model.eval()
        hooks = []
        
        def hook_fn(module, input, output):
            """收集激活值统计"""
            if isinstance(output, torch.Tensor):
                # 计算每个通道的激活值缩放
                scale = output.abs().mean(dim=(0, 2, 3) if len(output.shape) > 2 else 0)
                self.activation_scales[id(module)] = scale
        
        # 注册hook
        for module in self.model.modules():
            if isinstance(module, (nn.Conv2d, nn.Linear)):
                hooks.append(module.register_forward_hook(hook_fn))
        
        # 运行校准数据
        with torch.no_grad():
            self.model(calibration_data)
        
        # 移除hook
        for hook in hooks:
            hook.remove()
    
    def quantize_layer(self, layer: nn.Linear):
        """
        量化单个层
        
        参数:
            layer: 线性层
        """
        W = layer.weight.data.float()
        
        # 获取激活值缩放
        if id(layer) in self.activation_scales:
            act_scale = self.activation_scales[id(layer)].to(W.device)
        else:
            act_scale = torch.ones_like(W.mean(dim=1))
        
        # 考虑激活值缩放的量化
        W_scaled = W * act_scale.unsqueeze(1)
        
        max_val = W_scaled.abs().max()
        scale = max_val / (2 ** (self.bit_width - 1) - 1)
        
        W_quant = torch.clamp(
            torch.round(W_scaled / scale),
            -(2 ** (self.bit_width - 1)),
            2 ** (self.bit_width - 1) - 1
        )
        
        W_dequant = W_quant.float() * scale / act_scale.unsqueeze(1)
        layer.weight.data = W_dequant
