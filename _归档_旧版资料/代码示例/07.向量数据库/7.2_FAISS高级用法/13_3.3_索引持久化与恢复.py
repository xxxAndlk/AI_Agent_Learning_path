import faiss
import numpy as np
import pickle

class PersistentFAISS:
    """支持持久化的FAISS索引"""
    
    def __init__(self, index_file='faiss_index.bin', id_map_file='id_map.pkl'):
        self.index_file = index_file
        self.id_map_file = id_map_file
        self.index = None
        self.id_map = {}
        
    def save(self, index):
        """保存索引到文件"""
        # 保存FAISS索引
        faiss.write_index(index, self.index_file)
        
        # 保存ID映射
        with open(self.id_map_file, 'wb') as f:
            pickle.dump(self.id_map, f)
            
        print(f"索引已保存: {self.index_file}")
        
    def load(self):
        """从文件加载索引"""
        if os.path.exists(self.index_file):
            self.index = faiss.read_index(self.index_file)
            with open(self.id_map_file, 'rb') as f:
                self.id_map = pickle.load(f)
            print(f"索引已加载: {self.index.ntotal} 个向量")
            return self.index
        return None
    
    def save_or_load(self):
        """加载或创建新索引"""
        if os.path.exists(self.index_file):
            return self.load()
        else:
            self.index = faiss.IndexFlatL2(128)
            return self.index

# 使用示例
import os

persistent = PersistentFAISS()

# 尝试加载或创建新索引
index = persistent.save_or_load()

# 添加数据
vectors = np.random.random((10000, 128)).astype('float32')
index.add(vectors)

# 保存
persistent.save(index)

# 后续加载使用
# index = persistent.load()
