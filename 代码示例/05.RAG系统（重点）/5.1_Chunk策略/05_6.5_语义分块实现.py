# 语义分块根据文本的语义相似度来决定分割点
# 这种方法能够产生更符合语义边界的分块结果

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np

# 示例文本：包含不同主题的段落
semantic_text = """
今天天气很好，阳光明媚。我决定去公园散步，呼吸新鲜空气。
公园里有许多人在锻炼身体，有的跑步，有的打太极。
我还看到有人在喂鸽子，鸽子们在天空中自由飞翔。

机器学习是人工智能的核心技术。通过大量数据的训练，
机器可以自动学习规律并进行预测。深度学习是机器学习的分支，
使用多层神经网络来学习数据的层次化表示。
计算机视觉是深度学习的重要应用领域，包括图像分类、目标检测等任务。

午餐时间，我去了附近的餐厅。餐厅的环境很好，装修得很温馨。
我点了一份宫保鸡丁，味道非常不错。服务员的态度也很热情。
这家餐厅的招牌菜还有水煮鱼和麻婆豆腐，都很有特色。

自然语言处理技术近年来取得了显著进展。BERT、GPT等预训练模型
大幅提升了各种NLP任务的性能。问答系统、机器翻译、文本摘要等应用
已经广泛部署在实际场景中。Transformer架构是这些模型的基础。
"""

# 方法1：使用LangChain的SemanticChunker
# SemanticChunker使用embedding模型计算句子之间的相似度
# 当相似度低于阈值时进行分割

try:
    # 加载embedding模型
    # all-MiniLM-L6-v2是一个轻量级但效果不错的模型
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # 创建语义分块器
    # breakpoint_threshold_type：分割点判定策略，percentile表示按相似度分布的百分位
    # breakpoint_threshold_amount：阈值参数，值越低分割越细
    semantic_chunker = SemanticChunker(
        embeddings=embeddings,
        breakpoint_threshold_type="percentile",
        breakpoint_threshold_amount=95.0,
        add_start_index=True,  # 添加起始索引
    )
    
    # 执行语义分块
    semantic_chunks = semantic_chunker.split_text(semantic_text)
    
    print(f"语义分块结果：共 {len(semantic_chunks)} 个块\n")
    for i, chunk in enumerate(semantic_chunks):
        print(f"--- 块 {i+1} ---")
        print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
        print()
        
except ImportError as e:
    print("请安装必要的依赖：pip install langchain-experimental sentence-transformers")
