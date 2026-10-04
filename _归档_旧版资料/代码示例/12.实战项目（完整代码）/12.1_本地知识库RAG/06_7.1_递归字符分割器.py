# src/chunking/recursive_splitter.py
# 递归字符分割器
from typing import List, Optional, Callable
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class RecursiveTextSplitter:
    """递归字符文本分割器
    
    尝试按层次分割文本：
    1. 首先尝试在段落分割符处分割
    2. 然后在句子分割符处分割
    3. 最后在字符级分割
    
    优点：尽量在自然边界处分割，保持语义完整
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
        length_function: Callable[[str], int] = len,
        keep_separator: bool = False
    ):
        """
        参数:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 相邻块之间的重叠字符数
            separators: 分割符列表，按优先级排序
            length_function: 计算文本长度的函数
            keep_separator: 是否保留分割符
        """
        # 默认分割符：按优先级排序
        # 优先在更大的单元（段落）处分割
        if separators is None:
            separators = [
                "\n\n",      # 段落分隔（两个换行）
                "\n",        # 换行
                "。",        # 中文句号
                "！",        # 中文感叹号
                "？",        # 中文问号
                ". ",        # 英文句号+空格
                "! ",        # 英文感叹号+空格
                "? ",        # 英文问号+空格
                "; ",        # 分号
                ", ",        # 逗号
                " ",         # 空格
                ""           # 字符级分割（最后手段）
            ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators,
            length_function=length_function,
            keep_separator=keep_separator
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割Document列表
        
        参数:
            documents: 原始Document列表
        返回:
            分割后的Document列表
        """
        logger.info(f"开始分割 {len(documents)} 个文档")
        
        chunks = self.splitter.split_documents(documents)
        
        # 添加分割元数据
        for i, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = i
            chunk.metadata["chunking_method"] = "recursive"
        
        logger.info(f"分割完成，得到 {len(chunks)} 个文本块")
        return chunks
    
    def split_text(self, text: str) -> List[str]:
        """分割单个文本
        
        参数:
            text: 待分割的文本
        返回:
            文本块列表
        """
        return self.splitter.split_text(text)


class ChineseRecursiveSplitter:
    """针对中文优化的递归分割器
    
    中英文处理有差异：
    - 中文以字符为单位，没有明显的单词边界
    - 标点符号和换行是重要的分割边界
    - 需要特殊处理中文标点
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        # 中文优化分割符
        chinese_separators = [
            "\n\n",      # 段落
            "\n",        # 换行
            "。\n",      # 句号+换行
            "。",        # 句号
            "！",        # 感叹号
            "？",        # 问号
            "；",        # 分号
            "，",        # 逗号
            "、",        # 顿号
            " ",         # 空格（英文）
            ""           # 字符级
        ]
        
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=chinese_separators,
            length_function=self._chinese_length
        )
    
    @staticmethod
    def _chinese_length(text: str) -> int:
        """中文字符计长函数
        
        中文字符计为1，英文数字计为0.5
        这样可以更好地控制中英文混合文本的长度
        """
        length = 0
        for char in text:
            if '\u4e00' <= char <= '\u9fff':  # 中文
                length += 1
            elif char.isascii():  # ASCII字符
                length += 0.5
            else:  # 其他
                length += 1
        return int(length)
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割Document列表"""
        return self.splitter.split_documents(documents)


# 使用示例
if __name__ == "__main__":
    from src.loaders.directory_loader import UnifiedDocumentLoader
    
    # 加载文档
    loader = UnifiedDocumentLoader()
    docs = loader.load_directory("./data/docs")
    
    # 分割
    splitter = RecursiveTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)
    
    print(f"原始文档数: {len(docs)}")
    print(f"分割后块数: {len(chunks)}")
    
    # 显示前3个块
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- 块 {i+1} ---")
        print(f"内容 ({len(chunk.page_content)} 字符): {chunk.page_content[:100]}...")
        print(f"元数据: {chunk.metadata}")
