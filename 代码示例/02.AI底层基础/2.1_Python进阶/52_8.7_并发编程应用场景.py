from concurrent.futures import ThreadPoolExecutor
from typing import List

def load_batch(batch_indices: List[int], dataset) -> List:
    """加载一批数据"""
    return [dataset[i] for i in batch_indices]

class ConcurrentDataLoader:
    """并发数据加载器"""
    
    def __init__(self, dataset, batch_size: int, num_workers: int = 4):
        self.dataset = dataset
        self.batch_size = batch_size
        self.num_workers = num_workers
    
    def __iter__(self):
        indices = list(range(len(self.dataset)))
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            # 将数据分成多个批次，并发加载
            for i in range(0, len(indices), self.batch_size):
                batch_indices = indices[i:i+self.batch_size]
                # 分片提交到线程池
                yield executor.submit(load_batch, batch_indices, self.dataset)
