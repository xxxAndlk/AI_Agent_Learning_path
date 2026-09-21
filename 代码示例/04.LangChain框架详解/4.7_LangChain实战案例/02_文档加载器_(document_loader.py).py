"""
文档加载模块
支持多种格式文档的加载
"""
import logging
from pathlib import Path
from typing import List, Optional, Union
from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredHTMLLoader,
    UnstructuredMarkdownLoader,
    DirectoryLoader,
)
from langchain_core.documents import Document

logger = logging.getLogger(__name__)


class DocumentLoader:
    """文档加载器封装类"""
    
    # 文件扩展名到加载器的映射
    LOADER_MAPPING = {
        ".txt": TextLoader,
        ".md": UnstructuredMarkdownLoader,
        ".markdown": UnstructuredMarkdownLoader,
        ".pdf": PyPDFLoader,
        ".docx": Docx2txtLoader,
        ".html": UnstructuredHTMLLoader,
    }
    
    def __init__(self, encoding: str = "utf-8"):
        """
        初始化文档加载器
        
        Args:
            encoding: 文本编码格式
        """
        self.encoding = encoding
    
    def load_file(self, file_path: Union[str, Path]) -> List[Document]:
        """
        加载单个文件
        
        Args:
            file_path: 文件路径
            
        Returns:
            加载的文档列表
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        loader_class = self.LOADER_MAPPING.get(suffix)
        
        if loader_class is None:
            logger.warning(f"不支持的文件类型: {suffix}")
            return []
        
        try:
            # 根据文件类型选择加载器
            if suffix == ".pdf":
                loader = loader_class(str(path))
            elif suffix in [".txt"]:
                loader = loader_class(str(path), encoding=self.encoding)
            else:
                loader = loader_class(str(path))
            
            documents = loader.load()
            logger.info(f"成功加载文件: {path.name}, 包含 {len(documents)} 个文档块")
            return documents
            
        except Exception as e:
            logger.error(f"加载文件失败 {path.name}: {str(e)}")
            return []
    
    def load_directory(
        self,
        directory: Union[str, Path],
        glob_pattern: str = "**/*.*",
        ignore_patterns: Optional[List[str]] = None
    ) -> List[Document]:
        """
        加载目录下的所有支持的文件
        
        Args:
            directory: 目录路径
            glob_pattern: 文件匹配模式
            ignore_patterns: 忽略的文件模式
            
        Returns:
            所有加载的文档列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists() or not dir_path.is_dir():
            raise ValueError(f"目录不存在: {directory}")
        
        # 构建目录加载器
        loader = DirectoryLoader(
            str(dir_path),
            glob=glob_pattern,
            ignore_hidden=True,
            loader_kwargs={"encoding": self.encoding},
        )
        
        # 过滤不支持的文件类型
        documents = loader.load()
        
        # 过滤文档
        filtered_docs = [
            doc for doc in documents 
            if Path(doc.metadata.get("source", "")).suffix.lower() 
            in self.LOADER_MAPPING.keys()
        ]
        
        logger.info(
            f"从目录 {directory} 加载了 {len(filtered_docs)} 个文档"
        )
        return filtered_docs
