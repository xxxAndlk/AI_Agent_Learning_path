"""
文本分割模块
将长文档分割成较小的块以便嵌入
"""
import logging
from typing import List, Optional
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownTextSplitter,
    PythonCodeTextSplitter,
    HTMLHeaderTextSplitter,
)
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class TextSplitter:
    """文本分割器封装类"""
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: Optional[List[str]] = None,
        keep_separator: bool = True,
    ):
        """
        初始化文本分割器
        
        Args:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 块之间的重叠字符数
            separators: 自定义分隔符列表
            keep_separator: 是否保留分隔符
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators
        self.keep_separator = keep_separator
        
        # 创建默认的分隔符列表
        if self.separators is None:
            self.separators = [
                "\n\n",  # 段落分隔
                "\n",    # 行分隔
                "。",    # 中文句子
                "！",    # 中文感叹
                "？",    # 中文问号
                "；",    # 中文分号
                "，",    # 中文逗号
                " ",     # 英文空格
                "",
            ]
    
    def split_documents(
        self,
        documents: List[Document],
        split_by: str = "recursive",
    ) -> List[Document]:
        """
        分割文档
        
        Args:
            documents: 要分割的文档列表
            split_by: 分割方式 ("recursive", "markdown", "python", "html")
            
        Returns:
            分割后的文档列表
        """
        if not documents:
            return []
        
        # 根据分割方式选择合适的分割器
        if split_by == "recursive":
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.separators,
                keep_separator=self.keep_separator,
                length_function=len,
            )
        elif split_by == "markdown":
            splitter = MarkdownTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif split_by == "python":
            splitter = PythonCodeTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
            )
        elif split_by == "html":
            splitter = HTMLHeaderTextSplitter()
        else:
            raise ValueError(f"未知的分割方式: {split_by}")
        
        # 执行分割
        if split_by == "html":
            # HTML 分割器直接处理文本
            splits = []
            for doc in documents:
                splits.extend(splitter.split_text(doc.page_content))
        else:
            splits = splitter.split_documents(documents)
        
        logger.info(
            f"将 {len(documents)} 个文档分割为 {len(splits)} 个块"
        )
        
        return splits
    
    def split_text(
        self,
        text: str,
        split_by: str = "recursive",
    ) -> List[str]:
        """
        直接分割文本
        
        Args:
            text: 要分割的文本
            split_by: 分割方式
            
        Returns:
            分割后的文本块列表
        """
        if split_by == "recursive":
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                separators=self.separators,
                keep_separator=self.keep_separator,
                length_function=len,
            )
        else:
            raise ValueError(f"不支持的分割方式: {split_by}")
        
        return splitter.split_text(text)
