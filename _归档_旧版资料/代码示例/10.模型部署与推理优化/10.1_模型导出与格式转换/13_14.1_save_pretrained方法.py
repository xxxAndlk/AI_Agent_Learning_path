# 1. 需要安装transformers库
# pip install transformers torch

import torch                    # 2. 导入PyTorch
from transformers import AutoModel, AutoTokenizer, AutoModelForSequenceClassification  # 3. 导入Transformers

class HuggingFaceModelExporter:
    """HuggingFace模型导出器"""
    
    def __init__(self, model_name="bert-base-uncased"):
        """4. 初始化导出器
        
        参数:
            model_name: HuggingFace模型名称或本地路径
        """
        self.model_name = model_name
    
    def load_and_save_model(self, save_directory="./hf_model"):
        """5. 加载并保存模型
        
        save_pretrained会保存：
        - config.json: 模型配置
        - pytorch_model.bin 或 model.safetensors: 权重
        - tokenizer相关文件
        """
        # 6. 加载预训练模型
        # AutoModel自动识别模型类型
        model = AutoModel.from_pretrained(self.model_name)
        
        # 7. 保存模型到指定目录
        # 这会创建以下文件：
        # - config.json: 模型架构配置
        # - pytorch_model.bin/bin 或 safetensors: 模型权重
        # - vocab.json, tokenizer.json等: 分词器文件
        model.save_pretrained(save_directory)
        
        print(f"✅ 模型已保存到 {save_directory}")
        
        # 8. 同时保存tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        tokenizer.save_pretrained(save_directory)
        
        return model, tokenizer
    
    def load_and_save_classification_model(self, num_labels=2, save_dir="./hf_cls_model"):
        """9. 加载并保存分类模型
        
        用于文本分类、情感分析等任务
        """
        # 10. 加载专门用于分类的模型
        # AutoModelForSequenceClassification会自动添加分类头
        model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=num_labels
        )
        
        # 11. 保存模型和配置
        model.save_pretrained(save_dir)
        
        # 12. 保存tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        tokenizer.save_pretrained(save_dir)
        
        print(f"✅ 分类模型已保存到 {save_dir}")
        return model, tokenizer
    
    def export_to_torchscript(self, save_dir="./hf_torchscript"):
        """13. 导出为TorchScript格式
        
        HuggingFace模型也可以导出为TorchScript
        """
        # 14. 加载模型
        model = AutoModel.from_pretrained(self.model_name)
        model.eval()
        
        # 15. 创建示例输入
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # 16. 准备一个示例句子
        example_text = "This is a test sentence."
        inputs = tokenizer(example_text, return_tensors="pt")
        
        # 17. 使用torch.jit.trace导出
        traced_model = torch.jit.trace(
            model,
            (inputs['input_ids'], inputs['attention_mask'])
        )
        
        # 18. 保存
        import os
        os.makedirs(save_dir, exist_ok=True)
        traced_model.save(f"{save_dir}/model.pt")
        
        print(f"✅ TorchScript模型已保存到 {save_dir}")
        return traced_model
    
    def export_to_onnx(self, save_dir="./hf_onnx"):
        """19. 导出为ONNX格式
        
        使用transformers.onnx包导出
        """
        from transformers.onnx import export
        
        # 20. 加载模型和tokenizer
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        
        # 21. 准备模型用于ONNX导出
        model = AutoModel.from_pretrained(self.model_name)
        
        # 22. 创建输出目录
        import os
        os.makedirs(save_dir, exist_ok=True)
        
        # 23. 使用tokenizer获取示例输入
        example_text = "This is a test."
        inputs = tokenizer(example_text, return_tensors="pt")
        
        # 24. 导出为ONNX
        torch.onnx.export(
            model,
            (inputs['input_ids'], inputs['attention_mask']),
            f"{save_dir}/model.onnx",
            input_names=['input_ids', 'attention_mask'],
            output_names=['last_hidden_state'],
            dynamic_axes={
                'input_ids': {0: 'batch_size', 1: 'sequence_length'},
                'attention_mask': {0: 'batch_size', 1: 'sequence_length'},
                'last_hidden_state': {0: 'batch_size', 1: 'sequence_length'}
            }
        )
        
        print(f"✅ ONNX模型已保存到 {save_dir}")

def load_huggingface_model():
    """25. 加载保存的HuggingFace模型"""
    # 26. 加载模型
    model = AutoModel.from_pretrained("./hf_model")
    tokenizer = AutoTokenizer.from_pretrained("./hf_model")
    
    # 27. 使用模型进行推理
    text = "Hello, world!"
    inputs = tokenizer(text, return_tensors="pt")
    
    with torch.no_grad():
        outputs = model(**inputs)
    
    # 28. 获取最后隐藏状态
    last_hidden_state = outputs.last_hidden_state
    print(f"输出形状: {last_hidden_state.shape}")
    
    return model, tokenizer

def huggingface_to_deployment():
    """29. HuggingFace模型部署工作流
    
    完整的模型部署流程：
    1. 选择并加载预训练模型
    2. 可选：微调模型
    3. 导出为部署格式（TorchScript/ONNX）
    4. 部署到目标平台
    """
    print("\n=== HuggingFace 模型部署流程 ===")
    print("1. 选择模型: transformers-cli download bert-base-uncased")
    print("2. 微调（如需要）: 使用transformers的Trainer")
    print("3. 导出TorchScript: model.save_pretrained() + torch.jit.trace")
    print("4. 导出ONNX: torch.onnx.export 或 transformers.onnx.export")
    print("5. 部署: ONNX Runtime / TorchServe / vLLM等")

if __name__ == "__main__":
    # 30. 示例使用
    exporter = HuggingFaceModelExporter("bert-base-uncased")
    # exporter.load_and_save_model()
    # exporter.export_to_onnx()
    print("HuggingFace导出器已准备")
