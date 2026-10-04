# 使用plotly创建交互式可视化
import plotly.express as px
import pandas as pd
from sentence_transformers import SentenceTransformer

def interactive_visualization():
    """交互式嵌入可视化"""
    
    model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    
    # 数据
    data = {
        "category": ["科技"] * 3 + ["天气"] * 3 + ["食物"] * 3,
        "text": [
            "深度学习很重要", "机器学习是AI分支", "NLP很有趣",
            "今天天气好", "明天会下雨", "温度很高",
            "我爱吃苹果", "水果很甜", "美食令人愉悦"
        ]
    }
    
    df = pd.DataFrame(data)
    
    # 编码
    embeddings = model.encode(df["text"].tolist())
    
    # UMAP降维
    reducer = umap.UMAP(n_components=2, random_state=42)
    coords = reducer.fit_transform(embeddings)
    
    df["x"] = coords[:, 0]
    df["y"] = coords[:, 1]
    
    # 交互式图表
    fig = px.scatter(
        df,
        x="x",
        y="y",
        color="category",
        text="text",
        title="句子嵌入交互式可视化"
    )
    
    fig.update_traces(textposition='top center')
    fig.update_layout(height=600, width=800)
    
    # 保存为HTML
    fig.write_html("embeddings_interactive.html")
    print("交互式可视化已保存为 embeddings_interactive.html")

interactive_visualization()
