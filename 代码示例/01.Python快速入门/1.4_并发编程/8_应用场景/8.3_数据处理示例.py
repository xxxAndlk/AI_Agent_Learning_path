import numpy as np
# multiprocessing（并行数据处理）
from multiprocessing import Pool
import pandas as pd

def process_chunk(chunk):
    return chunk.apply(complex_transform)

if __name__ == '__main__':
    data = pd.read_csv('large_file.csv')
    chunks = np.array_split(data, 8)
    
    with Pool(8) as pool:
        results = pool.map(process_chunk, chunks)
