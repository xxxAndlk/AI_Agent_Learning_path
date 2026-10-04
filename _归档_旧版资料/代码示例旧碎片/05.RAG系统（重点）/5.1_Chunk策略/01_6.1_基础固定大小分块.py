# 导入必要的库
# RecursiveCharacterTextSplitter: LangChain提供的递归文本分割器
from langchain_text_splitters import RecursiveCharacterTextSplitter
# TextLoader: LangChain提供的文本加载器，用于读取文本文件
from langchain_community.document_loaders import TextLoader

# 创建示例文本文件（用于演示分块过程）
# 写入重复的示例文本以便观察分块效果
with open("example.txt", "w", encoding="utf-8") as f:
    f.write("这是一段示例文本。" * 100)  # 写入100个重复的示例文本

# 加载文本文件
# 创建TextLoader对象，指定文件路径和编码格式
loader = TextLoader("example.txt", encoding="utf-8")
# load()方法返回Document对象列表，每个Document包含page_content（文本内容）和metadata（元数据）
documents = loader.load()

# ============ 方法1：固定大小分块 ============
# RecursiveCharacterTextSplitter是LangChain中最常用的文本分割器
# 它会递归地按分隔符分割文本，优先尝试大分隔符，失败则尝试小分隔符
# 这样可以尽量在自然语言边界（如句子、段落）处切分，而不是在单词中间截断
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,                   # 每个块的目标大小（字符数）
                                        # 100字符约为25-50个中文词，适合大多数场景
    chunk_overlap=20,                 # 相邻块之间的重叠字符数（保持上下文连贯）
                                        # 重叠区域确保重要信息不会因切分而被完全隔开
    length_function=len,              # 计算长度的函数，默认使用len（字符数）
                                        # 也可以使用tiktoken等tokenizer按token计算
)

# 分割文档
# split_documents()方法接收Document对象列表，返回切分后的Document列表
chunks = text_splitter.split_documents(documents)
print("固定大小分块数量:", len(chunks))  # 打印分块数量
print("第一个块内容:", chunks[0].page_content)  # 打印第一个块的内容
