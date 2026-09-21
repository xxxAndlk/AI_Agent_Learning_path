import re                                   # 正则表达式，用于文本分割
from typing import List, Dict               # 类型提示
from dataclasses import dataclass           # 数据类装饰器

@dataclass
class DocumentChunk:
    """文档块数据结构"""
    content: str                           # 文档块内容
    metadata: Dict                         # 元数据（来源、位置等）
    chunk_id: str = ""                     # 块唯一标识


class DocumentChunker:
    """文档分块器
    
    提供多种分块策略来处理不同类型的文档
    """
    
    def __init__(
        self,
        chunk_size: int = 500,            # 每块最大字符数
        chunk_overlap: int = 50           # 块之间的重叠字符数
    ):
        """初始化分块器
        
        参数:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 相邻块之间的重叠字符数，用于保持上下文连贯
        """
        self.chunk_size = chunk_size       # 设置块大小
        self.chunk_overlap = chunk_overlap # 设置重叠大小
    
    def fixed_size_chunk(
        self,
        text: str,
        source: str = "unknown"
    ) -> List[DocumentChunk]:
        """固定长度分块
        
        参数:
            text: 待分割的文本
            source: 文档来源标识
        返回:
            文档块列表
        """
        chunks = []                        # 存储结果块
        start = 0                          # 当前起始位置
        chunk_index = 0                    # 块索引计数器
        
        # 循环切分直到文本结束
        while start < len(text):
            # 计算当前块的结束位置
            end = start + self.chunk_size
            
            # 如果不是最后一块，尝试在句子边界处截断
            if end < len(text):
                # 从end位置向前查找最近的句子结束符
                last_period = text.rfind('。', start, end)
                last_exclaim = text.rfind('！', start, end)
                last_question = text.rfind('？', start, end)
                
                # 取最近的句子结束符位置
                boundary = max(last_period, last_exclaim, last_question)
                
                # 如果找到句子边界且距离start不太近
                if boundary > start + 100:
                    end = boundary + 1     # 包含标点符号
            
            # 提取当前块内容
            chunk_content = text[start:end].strip()
            
            # 如果内容不为空，创建文档块
            if chunk_content:
                chunk = DocumentChunk(
                    content=chunk_content,
                    metadata={
                        "source": source,            # 来源标识
                        "chunk_index": chunk_index,   # 块序号
                        "start_char": start,          # 起始字符位置
                        "end_char": end               # 结束字符位置
                    },
                    chunk_id=f"{source}_chunk_{chunk_index}"  # 生成唯一ID
                )
                chunks.append(chunk)       # 添加到结果列表
                chunk_index += 1           # 递增索引
            
            # 计算下一块的起始位置（考虑重叠）
            start = end - self.chunk_overlap if end < len(text) else end
        
        return chunks                      # 返回所有文档块


def demonstrate_rag_data_building():
    """演示RAG数据构建流程"""
    
    print("=" * 60)
    print("RAG数据构建演示")
    print("=" * 60)
    
    # 示例文档
    sample_document = """
    人工智能是计算机科学的一个重要分支，致力于研究和开发用于模拟人类智能的系统。
    机器学习是人工智能的核心技术之一，它使计算机能够从数据中自动学习模式。
    深度学习是机器学习的一个子集，使用多层神经网络来学习数据的层次化表示。
    """
    
    # 创建分块器
    chunker = DocumentChunker(
        chunk_size=100,                   # 每块100字符
        chunk_overlap=20                  # 重叠20字符
    )
    
    # 固定长度分块
    print("\n--- 固定长度分块 ---")
    chunks = chunker.fixed_size_chunk(sample_document, source="ai_intro")
    print(f"生成 {len(chunks)} 个文档块")
    for i, chunk in enumerate(chunks):
        print(f"\n块 {i+1} (ID: {chunk.chunk_id}):")
        print(f"  长度: {len(chunk.content)} 字符")
        print(f"  内容: {chunk.content[:50]}...")


if __name__ == "__main__":
    demonstrate_rag_data_building()
