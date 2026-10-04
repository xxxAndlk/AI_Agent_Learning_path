# ThreadPoolExecutor - IO密集型
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch_url(url: str) -> dict:
    response = requests.get(url)
    return {"url": url, "status": response.status_code}

urls = ["https://example.com"] * 10

with ThreadPoolExecutor(max_workers=5) as executor:
    results = list(executor.map(fetch_url, urls))

# ProcessPoolExecutor - CPU密集型
from concurrent.futures import ProcessPoolExecutor
import numpy as np

def compute_matrix_product(size: int) -> np.ndarray:
    a = np.random.rand(size, size)
    b = np.random.rand(size, size)
    return np.dot(a, b)

sizes = [1000, 2000, 3000]

with ProcessPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(compute_matrix_product, sizes))
