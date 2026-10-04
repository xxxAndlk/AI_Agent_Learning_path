# 基于Token的分块是更精确的分块方式
# 因为大语言模型使用Token而不是字符来处理文本
# 1个Token约等于1-2个中文字符或3-4个英文字符

from langchain_text_splitters import RecursiveCharacterTextSplitter
import tiktoken  # OpenAI的Tokenizer库

# 加载Token计数器
# tiktoken提供多种编码方式：
# - cl100k_base: GPT-4与GPT-3.5系列使用的编码
# - o200k_base: GPT-4o及更新模型使用的编码
# - p50k_base: Codex使用的编码
# - r50k_base: GPT-3使用的编码
encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    """计算文本的token数量"""
    return len(encoding.encode(text))

# 示例文本
token_text = """
在自然语言处理领域，Transformer架构已经成为最重要的深度学习模型之一。
Transformer通过自注意力机制（Self-Attention）能够并行处理序列中的所有位置，
克服了传统循环神经网络无法并行计算的缺点。

自注意力机制的核心思想是计算序列中每个元素与其他元素之间的相关性。
通过_query_、_key_和_value_三个向量，模型可以学习到序列内部的依赖关系。
多头注意力（Multi-Head Attention）进一步增强了模型的表达能力，
它使用多组注意力头，每个头关注不同的特征。

GPT（Generative Pre-trained Transformer）是基于Transformer解码器的语言模型。
通过大规模预训练和微调，GPT能够完成各种自然语言任务，如文本生成、
问答、翻译等。ChatGPT就是基于GPT技术开发的对话系统。
"""

# 创建基于Token的分块器
# 使用tiktoken作为长度函数，实现精确的Token级别分块
token_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,           # 每个块100个Token，约为150-200个中文字符
    chunk_overlap=20,         # 重叠20个Token，保持上下文
    length_function=count_tokens,  # 使用token计数函数
    separators=["\n\n", "\n", "。", "？", "！", "；", "，", ""],
    keep_separator=True,
)

# 执行分块
token_chunks = token_splitter.split_text(token_text)

print(f"基于Token的分块：共 {len(token_chunks)} 个块\n")

for i, chunk in enumerate(token_chunks):
    token_count = count_tokens(chunk)
    char_count = len(chunk)
    print(f"[块{i+1}] {token_count}Tokens / {char_count}字符")
    print(f"内容: {chunk[:60].replace(chr(10), ' ')}...")
    print()
