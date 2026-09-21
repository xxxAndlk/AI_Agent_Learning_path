class ModelFormatComparison:
    """模型格式对比分析器"""
    
    @staticmethod
    def compare_all_formats():
        """1. 全面对比所有模型格式"""
        
        comparison_data = """
=== 深度学习模型格式全面对比 ===

| 格式 | 文件扩展名 | 优点 | 缺点 | 适用场景 |
|------|-----------|------|------|---------|
| **PyTorch (.pt/.pth)** | .pt, .pth | 1. 官方格式，兼容性最好<br>2. 保存完整模型结构<br>3. 调试方便 | 1. 依赖Python环境<br>2. 加载速度慢<br>3. 文件较大 | 研究、原型开发、<br>PyTorch到PyTorch |
| **TorchScript** | .pt | 1. 脱离Python运行<br>2. 支持C++部署<br>3. 性能优化 | 1. 不支持动态控制流<br>2. 部分算子不支持<br>3. 调试困难 | 生产环境、<br>C++部署、边缘设备 |
| **ONNX** | .onnx | 1. 跨平台支持<br>2. 多框架互转<br>3. 硬件加速支持 | 1. 算子支持有限<br>2. 精度可能损失<br>3. 导出可能失败 | 跨平台部署、<br>TensorRT、ONNX Runtime |
| **TensorRT** | .plan | 1. NVIDIA GPU最优性能<br>2. 量化支持<br>3. 深度优化 | 1. 仅限NVIDIA GPU<br>2. 需要额外构建<br>3. 精度可能损失 | NVIDIA GPU推理、<br>生产环境部署 |
| **GGUF** | .gguf | 1. CPU高效运行<br>2. 多量化选项<br>3. 内存占用低 | 1. 主要用于LLM<br>2. 不支持复杂模型<br>3. 社区维护 | 大语言模型CPU部署、<br>消费级硬件 |
| **Safetensors** | .safetensors | 1. 安全（不执行代码）<br>2. 加载快速<br>3. 内存映射支持 | 1. 主要用于存储<br>2. 需要转换工具<br>3. HuggingFace生态 | 模型存储分享、<br>HuggingFace集成 |

"""
        print(comparison_data)
    
    @staticmethod
    def compare_size_and_speed():
        """2. 文件大小和加载速度对比"""
        
        print("=== 文件大小对比（以BERT-base为例）===")
        print("| 格式 | 精度 | 文件大小 | 相对大小 |")
        print("|------|------|---------|---------|")
        print("| PyTorch | FP32 | ~420MB | 1x |")
        print("| PyTorch | FP16 | ~210MB | 0.5x |")
        print("| TorchScript | FP32 | ~420MB | 1x |")
        print("| TorchScript | FP16 | ~210MB | 0.5x |")
        print("| ONNX | FP32 | ~410MB | ~1x |")
        print("| ONNX | FP16 | ~205MB | ~0.5x |")
        print("| GGUF Q4 | 4bit | ~175MB | ~0.4x |")
        print("| GGUF Q5 | 5bit | ~220MB | ~0.5x |")
        
        print("\n=== 加载速度对比 ===")
        print("| 格式 | 首次加载 | 后续加载 |")
        print("|------|---------|---------|")
        print("| PyTorch .pt | ~2s | ~2s |")
        print("| Safetensors | ~0.5s | ~0.1s |")
        print("| TorchScript | ~1s | ~1s |")
        print("| ONNX Runtime | ~3s | ~0.5s |")
        print("| GGUF | ~1s | ~0.3s |")
    
    @staticmethod
    def compare_inference_speed():
        """3. 推理速度对比（相对值）"""
        
        print("\n=== 推理速度对比（相对值，以PyTorch为基准）===")
        print("| 格式 | 设备 | 加速比 |")
        print("|------|------|-------|")
        print("| PyTorch | CPU | 1.0x |")
        print("| TorchScript | CPU | 1.1-1.3x |")
        print("| ONNX Runtime (CPU) | CPU | 1.0-1.5x |")
        print("| ONNX Runtime (CUDA) | GPU | 2-5x |")
        print("| TensorRT (FP32) | GPU | 3-6x |")
        print("| TensorRT (FP16) | GPU | 5-10x |")
        print("| TensorRT (INT8) | GPU | 8-15x |")
        print("| GGUF Q4 | CPU | 4-8x vs PyTorch CPU |")

def format_selection_guide():
    """4. 模型格式选择指南
    
    根据不同的场景推荐合适的格式
    """
    
    scenarios = """
=== 场景化模型格式选择指南 ===

🔬 场景1：研究与实验
├── 推荐格式：PyTorch (.pt)
├── 原因：调试方便，原生支持
└── 使用方法：
    torch.save(model.state_dict(), 'model.pth')
    model = ModelClass()
    model.load_state_dict(torch.load('model.pth'))

🏭 场景2：生产环境服务（Python后端）
├── 推荐格式：TorchScript
├── 原因：脱离Python GIL，提升并发性能
└── 使用方法：
    traced = torch.jit.trace(model, input)
    traced.save('model.pt')

🌐 场景3：跨平台部署
├── 推荐格式：ONNX
├── 原因：支持Python/C++/Java/JS/移动端
└── 支持的运行时：
    - ONNX Runtime（多平台）
    - TensorRT（NVIDIA）
    - CoreML（Apple）
    - ONNX.js（浏览器）

🚀 场景4：NVIDIA GPU生产部署
├── 推荐格式：TensorRT
├── 原因：最高性能，深度优化
└── 优化选项：
    - FP16：2-3x加速
    - INT8：3-4x加速（需校准）
    - 算子融合：自动优化

💻 场景5：CPU部署/边缘设备
├── 推荐格式1：TorchScript（通用）
├── 推荐格式2：GGUF（大语言模型）
├── 原因：内存占用低，无需GPU
└── 量化选项：
    - GGUF Q4：最小内存
    - GGUF Q5：平衡选择

📱 场景6：移动端/嵌入式
├── 推荐格式1：ONNX + ONNX Runtime Mobile
├── 推荐格式2：CoreML（iOS）
├── 推荐格式3：TFLite（Android）
└── 特点：模型需要量化精简

🤖 场景7：大语言模型本地部署
├── 推荐格式：GGUF
├── 原因：CPU高效，量化支持好
├── 使用工具：llama.cpp
└── 量化方法：Q4_0, Q5_1, Q8_0等

📦 场景8：模型分享与存储
├── 推荐格式：Safetensors
├── 原因：安全、快速、内存映射
└── 使用方法：
    from safetensors.torch import save_file
    save_file(state_dict, 'model.safetensors')
"""
    
    print(scenarios)

def decision_tree():
    """5. 格式选择决策树"""
    
    print("""
=== 模型格式选择决策树 ===

开始
  │
  ├─ 目标运行环境是什么？
  │    │
  │    ├─ Python环境 → PyTorch (.pt) 或 Safetensors
  │    │
  │    ├─ C++/无Python → TorchScript
  │    │
  │    ├─ 浏览器/Web → ONNX + ONNX.js
  │    │
  │    ├─ NVIDIA GPU → TensorRT 或 ONNX + TensorRT
  │    │
  │    ├─ Apple设备 → CoreML 或 ONNX
  │    │
  │    ├─ Android → TFLite 或 ONNX
  │    │
  │    ├─ CPU/边缘 → TorchScript 或 GGUF（LLM）
  │    │
  │    └─ 多平台 → ONNX
  │
  ├─ 是否需要量化？
  │    │
  │    ├─ 是（LLM）→ GGUF
  │    │
  │    ├─ 是（视觉/NLP）→ TensorRT INT8 或 ONNX量化
  │    │
  │    └─ 否 → 原始格式
  │
  └─ 模型类型？
       │
       ├─ 大语言模型 → GGUF
       │
       ├─ 视觉模型 → TorchScript/ONNX/TensorRT
       │
       └─ 传统ML → ONNX或平台特定格式

结束
""")

def practical_recommendations():
    """6. 实际项目建议"""
    
    recommendations = """
=== 实际项目中的推荐策略 ===

📋 策略1：多格式保存
建议保存多种格式，以适配不同部署场景：
- PyTorch原始格式：用于继续训练/微调
- TorchScript：用于生产Python服务
- ONNX：用于跨平台部署
- GGUF（如适用）：用于本地LLM部署

📋 策略2：渐进式优化
1. 先用PyTorch验证模型正确性
2. 导出TorchScript/ONNX进行性能测试
3. 如需GPU加速，使用TensorRT
4. 如需CPU部署，考虑量化

📋 策略3：测试驱动
在导出后务必验证：
1. 输出精度：与原模型对比
2. 性能基准：延迟和吞吐量
3. 边界情况：空输入、异常值等

📋 策略4：版本管理
- 记录导出的PyTorch版本
- 记录ONNX opset版本
- 记录目标运行时的版本
- 保持一致性便于问题排查
"""
    
    print(recommendations)

if __name__ == "__main__":
    comparator = ModelFormatComparison()
    comparator.compare_all_formats()
    comparator.compare_size_and_speed()
    comparator.compare_inference_speed()
    format_selection_guide()
    decision_tree()
    practical_recommendations()
