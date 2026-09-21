class HFModelOptimizer:
    """HuggingFace模型推理优化器"""
    
    @staticmethod
    def optimize_inference(model, use_quantization=False):
        """31. 推理优化方法
        
        优化技术：
        1. 量化：减少模型大小，加速推理
        2. 编译：使用Torch Compile
        3. 容器化：使用ONNX Runtime
        """
        # 32. 启用量化（需要bitsandbytes库）
        if use_quantization:
            try:
                from transformers import BitsAndBytesConfig
                
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,    # 8位量化
                    # load_in_4bit=True   # 4位量化
                )
                
                # 重新加载模型为量化版本
                model = AutoModel.from_pretrained(
                    "bert-base-uncased",
                    quantization_config=quantization_config,
                    device_map="auto"
                )
                print("✅ 8位量化已启用")
            except ImportError:
                print("请安装bitsandbytes: pip install bitsandbytes")
        
        # 33. 使用Torch Compile加速（PyTorch 2.0+）
        try:
            model = torch.compile(model)
            print("✅ Torch Compile已启用")
        except Exception as e:
            print(f"Torch Compile不可用: {e}")
        
        return model
    
    @staticmethod
    def dynamic_batching(tokenizer, model, texts, max_batch_size=8):
        """34. 动态批处理
        
        将多个短文本打包成一个批次处理，提高吞吐量
        """
        # 35. 批量编码
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors="pt"
        )
        
        # 36. 分批处理（如果文本过长）
        if inputs['input_ids'].shape[0] > max_batch_size:
            outputs = []
            for i in range(0, len(texts), max_batch_size):
                batch = {k: v[i:i+max_batch_size] for k, v in inputs.items()}
                with torch.no_grad():
                    output = model(**batch)
                    outputs.append(output.logits)
            return torch.cat(outputs, dim=0)
        
        # 37. 单批次处理
        with torch.no_grad():
            outputs = model(**inputs)
        
        return outputs.logits

def benchmark_hf_optimization():
    """38. HuggingFace模型性能基准测试"""
    import time
    
    # 39. 测试配置
    model_name = "bert-base-uncased"
    test_texts = ["This is a test sentence."] * 100
    
    print("=== HuggingFace 性能测试 ===")
    print("1. 基础推理")
    print("2. Torch Compile")
    print("3. ONNX Runtime")
    print("4. 量化推理")

if __name__ == "__main__":
    optimizer = HFModelOptimizer()
    benchmark_hf_optimization()
