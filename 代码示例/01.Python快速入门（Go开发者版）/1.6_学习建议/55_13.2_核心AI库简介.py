# 1. NumPy - 数值计算基础
import numpy as np

# 类似于 Go 的切片，但支持多维和高级操作
arr = np.array([1, 2, 3, 4, 5])
matrix = np.array([[1, 2], [3, 4]])

# 向量化操作（无需循环）
result = arr * 2           # [2, 4, 6, 8, 10]
result = np.dot(matrix, matrix)  # 矩阵乘法

# 2. Pandas - 数据处理
import pandas as pd

# 读取数据
df = pd.read_csv("data.csv")

# 数据清洗
df = df.dropna()           # 删除空值
df = df.fillna(0)          # 填充空值

# 数据分析
stats = df.describe()      # 统计摘要
grouped = df.groupby("category").sum()  # 分组聚合

# 3. Matplotlib - 可视化
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot([1, 2, 3], [4, 5, 6])
plt.title("示例图表")
plt.xlabel("X轴")
plt.ylabel("Y轴")
plt.show()

# 4. PyTorch - 深度学习
import torch
import torch.nn as nn

# 定义神经网络
class NeuralNet(nn.Module):
    def __init__(self, input_size, hidden_size, num_classes):
        super().__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, num_classes)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out

# 训练
model = NeuralNet(784, 256, 10)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 5. Transformers - Hugging Face
from transformers import pipeline

# 使用预训练模型
classifier = pipeline("sentiment-analysis")
result = classifier("I love this product!")
# [{'label': 'POSITIVE', 'score': 0.99...}]
