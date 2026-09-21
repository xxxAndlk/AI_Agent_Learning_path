import cProfile
import pstats
import io

def profile_model_inference():
    """分析模型推理性能"""
    import numpy as np
    
    # 模拟模型推理
    def run_inference():
        data = np.random.rand(1, 3, 224, 224)
        for _ in range(100):
            # 模拟推理计算
            result = np.dot(data, data.transpose(0, 2, 1, 3))
        return result
    
    profiler = cProfile.Profile()
    profiler.enable()
    
    run_inference()
    
    profiler.disable()
    
    stream = io.StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)
    
    print(stream.getvalue())

if __name__ == "__main__":
    profile_model_inference()
