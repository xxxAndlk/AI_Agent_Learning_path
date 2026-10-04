# 1. 安装safetensors
# pip install safetensors

import torch                    # 2. 导入PyTorch
import safetensors.torch        # 3. 导入safetensors的PyTorch扩展

class SafetensorsExample:
    """Safetensors格式使用示例"""
    
    @staticmethod
    def save_model(model, save_path="model.safetensors"):
        """4. 使用safetensors保存模型
        
        优点：
        1. 安全：不执行任意代码
        2. 快速：零拷贝加载
        3. 内存映射：按需加载，节省内存
        4. 原子写入：防止文件损坏
        """
        # 5. 从模型获取state_dict
        state_dict = model.state_dict()
        
        # 6. 使用safetensors保存
        # safetensors.torch.save_file是推荐的方法
        safetensors.torch.save_file(state_dict, save_path)
        
        print(f"✅ 模型已保存为Safetensors格式: {save_path}")
        
        # 7. 获取文件大小
        import os
        size_mb = os.path.getsize(save_path) / (1024 * 1024)
        print(f"   文件大小: {size_mb:.2f} MB")
        
        return save_path
    
    @staticmethod
    def load_model(model, save_path="model.safetensors"):
        """8. 加载Safetensors格式的模型"""
        # 9. 使用safetensors加载
        # 可以直接加载到CPU或GPU
        state_dict = safetensors.torch.load_file(save_path)
        
        # 10. 加载到模型
        model.load_state_dict(state_dict)
        
        print(f"✅ Safetensors模型已加载")
        
        return model
    
    @staticmethod
    def load_to_device(save_path="model.safetensors", device="cuda"):
        """11. 直接加载到指定设备
        
        支持直接加载到GPU，减少CPU内存占用
        """
        # 12. 直接加载到CUDA设备
        state_dict = safetensors.torch.load_file(save_path, device=device)
        
        print(f"✅ 已加载到设备: {device}")
        
        return state_dict
    
    @staticmethod
    def partial_load(model, save_path="model.safetensors", keys=None):
        """13. 部分加载模型权重
        
        适用于：
        - 加载部分预训练权重
        - 微调时只加载部分层
        """
        # 14. 加载全部权重
        full_state_dict = safetensors.torch.load_file(save_path)
        
        if keys is not None:
            # 15. 只保留指定的键
            filtered_state_dict = {
                k: v for k, v in full_state_dict.items() 
                if k in keys
            }
        else:
            filtered_state_dict = full_state_dict
        
        # 16. 加载到模型（strict=False允许部分加载）
        model.load_state_dict(filtered_state_dict, strict=False)
        
        print(f"✅ 部分权重已加载")
        
        return model
    
    @staticmethod
    def compare_with_pickle():
        """17. Safetensors vs Pickle 性能对比"""
        import time
        import tempfile
        
        # 18. 创建测试模型
        model = torch.nn.Sequential(
            torch.nn.Linear(768, 768),
            torch.nn.ReLU(),
            torch.nn.Linear(768, 768),
            torch.nn.ReLU(),
            torch.nn.Linear(768, 30522)  # BERT词表大小
        )
        
        with tempfile.NamedTemporaryFile(suffix=".safetensors", delete=False) as f:
            sf_path = f.name
        
        with tempfile.NamedTemporaryFile(suffix=".pt", delete=False) as f:
            pt_path = f.name
        
        # 19. 保存为Safetensors
        start = time.time()
        safetensors.torch.save_file(model.state_dict(), sf_path)
        sf_time = time.time() - start
        
        # 20. 保存为Pickle
        start = time.time()
        torch.save(model.state_dict(), pt_path)
        pt_time = time.time() - start
        
        # 21. 加载Safetensors
        start = time.time()
        _ = safetensors.torch.load_file(sf_path)
        sf_load_time = time.time() - start
        
        # 22. 加载Pickle
        start = time.time()
        _ = torch.load(pt_path)
        pt_load_time = time.time() - start
        
        print("\n=== Safetensors vs Pickle 性能对比 ===")
        print(f"保存 - Safetensors: {sf_time:.4f}s, Pickle: {pt_time:.4f}s")
        print(f"加载 - Safetensors: {sf_load_time:.4f}s, Pickle: {pt_load_time:.4f}s")
        
        # 23. 清理
        import os
        os.remove(sf_path)
        os.remove(pt_path)

    @staticmethod
    def hf_integration():
        """24. HuggingFace集成
        
        Transformers库原生支持Safetensors格式
        """
        from transformers import AutoModel
        
        # 25. 加载模型时会自动使用Safetensors（如果可用）
        # 自动检测.safetensors或.bin文件
        
        # 26. 强制使用Safetensors
        # from transformers import AutoModel
        # model = AutoModel.from_pretrained(
        #     "model_name",
        #     local_files_only=False,
        #     use_safetensors=True  # 强制使用
        # )
        
        # 27. 保存模型为Safetensors
        # model.save_pretrained("output_dir", safe_serialization=True)
        
        print("\n=== HuggingFace Safetensors 集成 ===")
        print("加载: AutoModel.from_pretrained() 自动使用")
        print("保存: save_pretrained(safe_serialization=True)")

def convert_to_safetensors():
    """28. 将现有模型转换为Safetensors格式"""
    # 29. 从PyTorch检查点转换
    # 可以将.pth, .pt文件转换为.safetensors
    
    print("=== 转换为Safetensors ===")
    print("方法1: 使用safetensors命令行工具")
    print("  safetensors-convert input.pt output.safetensors")
    print("\n方法2: Python代码")
    print("""
import torch
import safetensors.torch

# 加载
state_dict = torch.load('model.pt')
# 保存
safetensors.torch.save_file(state_dict, 'model.safetensors')
    """)

if __name__ == "__main__":
    example = SafetensorsExample()
    example.compare_with_pickle()
    example.hf_integration()
    convert_to_safetensors()
