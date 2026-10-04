import umap
import matplotlib.pyplot as plt
import numpy as np

def visualize_umap(embeddings, words, labels):
    """UMAP可视化"""
    
    # UMAP降维
    reducer = umap.UMAP(
        n_components=2,
        n_neighbors=10,
        min_dist=0.1,
        metric='cosine',
        random_state=42
    )
    
    embeddings_2d = reducer.fit_transform(embeddings)
    
    # 绘图
    plt.figure(figsize=(12, 8))
    
    unique_labels = list(set(labels))
    colors = plt.cm.Set1(np.linspace(0, 1, len(unique_labels)))
    
    for label, color in zip(unique_labels, colors):
        mask = [l == label for l in labels]
        x = embeddings_2d[mask, 0]
        y = embeddings_2d[mask, 1]
        
        plt.scatter(x, y, c=[color], label=label, s=100, alpha=0.7)
    
    plt.legend()
    plt.title("词嵌入UMAP可视化")
    plt.savefig("word_embeddings_umap.png", dpi=150, bbox_inches='tight')
    plt.show()

# 示例：句子嵌入可视化
def visualize_sentence_embeddings():
    """句子嵌入可视化"""
    
    from sentence_transformers import SentenceTransformer
    
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # 准备句子
    sentences = [
        # 科技
        "深度学习是人工智能的核心",
        "机器学习算法非常重要",
        "Transformer模型改变了NLP",
        # 天气
        "今天天气真不错",
        "明天可能会下雨",
        "今天温度很高",
        # 食物
        "我很喜欢吃苹果",
        "这个水果很甜",
        "我喜欢美食",
    ]
    
    labels = [
        "科技", "科技", "科技",
        "天气", "天气", "天气",
        "食物", "食物", "食物",
    ]
    
    # 编码
    embeddings = model.encode(sentences)
    
    # 可视化
    visualize_umap(embeddings, sentences, labels)

visualize_sentence_embeddings()
