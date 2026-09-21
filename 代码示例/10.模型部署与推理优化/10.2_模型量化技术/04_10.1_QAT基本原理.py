class QATTrainer:
    """量化感知训练器"""
    
    def __init__(
        self,
        model: nn.Module,
        train_loader,
        quant_config: dict = None
    ):
        """
        初始化QAT训练器
        
        参数:
            model: 模型
            train_loader: 训练数据加载器
            quant_config: 量化配置
        """
        self.model = model
        self.train_loader = train_loader
        self.quant_config = quant_config or {
            'qscheme': torch.per_tensor_symmetric,
            'dtype': torch.qint8,
            'reduce_range': False
        }
    
    def prepare_qat_model(self) -> nn.Module:
        """
        准备QAT模型
        
        返回:
            准备好的模型
        """
        # 设置QAT配置
        self.model.qconfig = torch.quantization.get_default_qat_qconfig('fbgemm')
        
        # 准备模型
        torch.quantization.prepare_qat(self.model, inplace=True)
        
        return self.model
    
    def train(
        self,
        num_epochs: int = 10,
        learning_rate: float = 0.001
    ):
        """
        执行QAT训练
        
        参数:
            num_epochs: 训练轮数
            learning_rate: 学习率
        """
        optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=learning_rate
        )
        
        criterion = nn.CrossEntropyLoss()
        
        self.model.train()
        
        for epoch in range(num_epochs):
            total_loss = 0
            for batch_idx, (data, target) in enumerate(self.train_loader):
                optimizer.zero_grad()
                
                # 前向传播（包含伪量化）
                output = self.model(data)
                loss = criterion(output, target)
                
                # 反向传播（使用全精度梯度）
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            avg_loss = total_loss / len(self.train_loader)
            print(f"Epoch {epoch+1}/{num_epochs}, Loss: {avg_loss:.4f}")
    
    def convert_to_quantized(self) -> nn.Module:
        """
        转换为真正的量化模型
        
        返回:
           量化后的模型
        """
        self.model.eval()
        
        # 转换为量化模型（convert应作用于模块本身而非state_dict；
        # qconfig已在prepare_qat_model中设置，无需传qconfig_override）
        quantized_model = torch.quantization.convert(
            self.model.cpu(),
            inplace=False
        )
        
        return quantized_model
