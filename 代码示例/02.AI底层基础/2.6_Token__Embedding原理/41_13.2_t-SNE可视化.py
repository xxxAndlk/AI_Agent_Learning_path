import numpy as np
import matplotlib.pyplot as plt
from sklearn.manifold import TSNE
from sklearn.datasets import fetch_20newsgroups
from transformers import AutoTokenizer, AutoModel
import torch

def get_word_embeddings():
    """获取词嵌入进行可视化"""
    
    # 加载BERT
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    model = AutoModel.from_pretrained("bert-base-chinese")
    model.eval()
    
    # 词汇表中的词（取样）
    words = [
        "猫", "狗", "兔子", "老鼠",  # 动物
        "苹果", "香蕉", "橙子", "葡萄",  # 水果
        "汽车", "火车", "飞机", "轮船",  # 交通工具
        "国王", "皇后", "王子", "公主",  # 皇室
        "男人", "女人", "男孩", "女孩",  # 性别
    ]
    
    # 获取嵌入
    embeddings = []
    
    for word in words:
        inputs = tokenizer(word, return_tensors="pt", padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        # 使用[CLS]或平均
        emb = outputs.last_hidden_state[:, 0, :].numpy()
        embeddings.append(emb[0])
    
    return np.array(embeddings), words

def visualize_tsne():
    """t-SNE可视化"""
    
    embeddings, words = get_word_embeddings()
    
    print(f"原始维度: {embeddings.shape}")
    
    # t-SNE降维
    tsne = TSNE(n_components=2, random_state=42, perplexity=5)
    embeddings_2d = tsne.fit_transform(embeddings)
    
    print(f"降维后维度: {embeddings_2d.shape}")
    
    # 分类标签
    categories = {
        "动物": [0, 1, 2, 3],
        "水果": [4, 5, 6, 7],
        "交通工具": [8, 9, 10, 11],
        "皇室": [12, 13, 14, 15],
        "性别": [16, 17, 18, 19],
    }
    
    colors = ['#e74c3c', '#2ecc71', '#3498db', '#9b59b6', '#f39c12']
    
    # 绘图
    plt.figure(figsize=(12, 8))
    
    for (category, indices), color in zip(categories.items(), colors):
        x = embeddings_2d[indices, 0]
        y = embeddings_2d[indices, 1]
        plt.scatter(x, y, c=color, label=category, s=100)
        
        for i, idx in enumerate(indices):
            plt.annotate(words[idx], (x[i], y[i]), fontsize=10)
    
    plt.legend()
    plt.title("词嵌入t-SNE可视化")
    plt.savefig("word_embeddings_tsne.png", dpi=150, bbox_inches='tight')
    plt.show()

visualize_tsne()
