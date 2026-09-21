from typing import TypeVar, Generic, Protocol
import numpy as np

T = TypeVar('T', bound=np.ndarray)

class DataProcessor(Generic[T]):
    """数据处理器泛型类"""
    
    def process(self, data: T) -> T:
        """处理数据，返回相同类型"""
        return data * 2

# 具体实现
class ImageProcessor(DataProcessor[np.ndarray]):
    """图像处理器"""
    
    def process(self, image: np.ndarray) -> np.ndarray:
        # 图像特定处理
        return image / 255.0
