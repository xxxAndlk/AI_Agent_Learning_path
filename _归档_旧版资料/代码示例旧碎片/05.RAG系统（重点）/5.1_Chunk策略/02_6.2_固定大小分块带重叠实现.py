# 固定大小分块带重叠的详细实现
# 这种方法通过在相邻块之间保留重叠区域来保持上下文连贯性

from langchain_text_splitters import RecursiveCharacterTextSplitter

# 示例文本：一篇关于机器学习的文章
sample_text = """
机器学习是人工智能的一个分支，专门研究计算机怎样模拟或实现人类的学习行为，
以获取新的知识或技能，重新组织已有的知识结构使之不断改善自身的性能。
机器学习是人工智能的核心，是使计算机具有智能的根本途径。

深度学习是机器学习的一个分支，它是一种以人工神经网络为架构，
对数据进行表征学习的算法。深度学习在计算机视觉、语音识别、自然语言处理
等领域取得了突破性进展。

卷积神经网络是一种专门用来处理具有类似网格结构数据的神经网络，
例如图像数据（可以看作二维的像素网格）。卷积神经网络在图像分类、目标检测
等领域表现出色。

循环神经网络是一类以序列数据为输入，在序列的演进方向进行递归，
且所有节点按链式连接的递归神经网络。循环神经网络在自然语言处理、时间序列
预测等任务中广泛应用。

Transformer是一种基于自注意力机制的神经网络架构，
由Google在2017年提出。Transformer在机器翻译、文本生成等任务中
取得了 state-of-the-art 的效果。
"""

# 创建带重叠的固定大小分块器
# 参数说明：
# - chunk_size: 每个块的最大字符数
# - chunk_overlap: 相邻块之间的重叠字符数，这个值不能超过chunk_size
# - separator: 分隔符列表，按优先级排序
fixed_splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,           # 每个块200字符，适合中文文档
    chunk_overlap=50,         # 重叠50字符，约25%的重叠率
    separators=["\n\n", "\n", "。", "！", "？", "；", ""],  # 中文分隔符
    length_function=len,      # 按字符数计算长度
)

# 执行分块
fixed_chunks = fixed_splitter.split_text(sample_text)

# 打印分块结果
print(f"总共生成了 {len(fixed_chunks)} 个文本块\n")

for i, chunk in enumerate(fixed_chunks):
    print(f"--- 块 {i+1} (长度: {len(chunk)} 字符) ---")
    print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    print()
