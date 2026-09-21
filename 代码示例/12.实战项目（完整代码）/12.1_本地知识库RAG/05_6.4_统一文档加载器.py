# src/loaders/directory_loader.py
# 统一文档加载器
from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import DirectoryLoader, TextLoader

from .pdf_loader import PDFDocumentLoader
from .word_loader import WordDocumentLoader
from .markdown_loader import MarkdownDocumentLoader
import logging

logger = logging.getLogger(__name__)

class UnifiedDocumentLoader:
    """统一文档加载器
    
    支持多种文档格式的自动识别和加载
    内部根据文件扩展名自动选择合适的加载器
    """
    
    # 支持的文件扩展名映射
    LOADER_MAP = {
        ".txt": "text",
        ".pdf": "pdf",
        ".docx": "word",
        ".doc": "word_legacy",
        ".md": "markdown",
        ".markdown": "markdown",
    }
    
    def __init__(self):
        """初始化各类型加载器"""
        self.pdf_loader = PDFDocumentLoader(loader_type="pymupdf")
        self.word_loader = WordDocumentLoader(loader_type="docx2txt")
        self.markdown_loader = MarkdownDocumentLoader(loader_type="unstructured")
    
    def load(self, file_path: str) -> List[Document]:
        """加载单个文件，根据扩展名自动选择加载器
        
        参数:
            file_path: 文件路径
        返回:
            Document列表
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        suffix = path.suffix.lower()
        loader_type = self.LOADER_MAP.get(suffix)
        
        if loader_type is None:
            logger.warning(f"不支持的文件类型: {suffix}")
            return []
        
        logger.info(f"使用 {loader_type} 加载器加载: {file_path}")
        
        if loader_type == "text":
            return self._load_text(file_path)
        elif loader_type == "pdf":
            return self.pdf_loader.load_pdf(file_path)
        elif loader_type == "word":
            return self.word_loader.load_docx(file_path)
        elif loader_type == "word_legacy":
            return self._load_legacy_word(file_path)
        elif loader_type == "markdown":
            return self.markdown_loader.load_md(file_path)
        
        return []
    
    def _load_text(self, file_path: str) -> List[Document]:
        """加载纯文本文件"""
        loader = TextLoader(file_path, encoding="utf-8")
        documents = loader.load()
        
        # 添加元数据
        path = Path(file_path)
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_type"] = "text"
            doc.metadata["file_name"] = path.name
        
        return documents
    
    def _load_legacy_word(self, file_path: str) -> List[Document]:
        """加载旧版Word文档"""
        from .word_loader import LegacyWordLoader
        
        # 转换为docx
        converter = LegacyWordLoader()
        docx_path = converter.convert_to_docx(file_path)
        
        # 加载转换后的文档
        return self.word_loader.load_docx(docx_path)
    
    def load_directory(
        self,
        directory: str,
        recursive: bool = True,
        extensions: Optional[List[str]] = None
    ) -> List[Document]:
        """从目录加载所有支持的文件
        
        参数:
            directory: 目录路径
            recursive: 是否递归搜索子目录
            extensions: 指定要加载的文件扩展名列表，None表示加载所有支持类型
        返回:
            所有Document列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        if not dir_path.is_dir():
            raise ValueError(f"不是有效目录: {directory}")
        
        all_documents = []
        
        # 确定要搜索的扩展名
        if extensions:
            # 确保扩展名以点开头
            extensions = [ext if ext.startswith(".") else f".{ext}" for ext in extensions]
            # 过滤不支持的类型
            extensions = [ext for ext in extensions if ext in self.LOADER_MAP]
        else:
            # 使用所有支持的扩展名
            extensions = list(self.LOADER_MAP.keys())
        
        logger.info(f"搜索扩展名: {extensions}")
        
        # 查找所有匹配的文件
        if recursive:
            files = []
            for ext in extensions:
                files.extend(list(dir_path.rglob(f"*{ext}")))
        else:
            files = []
            for ext in extensions:
                files.extend(list(dir_path.glob(f"*{ext}")))
        
        logger.info(f"找到 {len(files)} 个文件")
        
        # 加载所有文件
        for file_path in files:
            try:
                documents = self.load(str(file_path))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"加载文件失败 {file_path}: {e}")
        
        logger.info(f"共加载 {len(all_documents)} 个文档块")
        return all_documents


# LangChain DirectoryLoader包装器
class SmartDirectoryLoader:
    """智能目录加载器
    
    使用LangChain的DirectoryLoader作为基础
    适用于简单的场景
    """
    
    @staticmethod
    def load(
        directory: str,
        glob_pattern: str = "**/*.*",
        loader_kwargs: Optional[dict] = None
    ) -> List[Document]:
        """使用DirectoryLoader加载目录
        
        参数:
            directory: 目录路径
            glob_pattern: glob模式
            loader_kwargs: 传递给加载器的参数
        返回:
            Document列表
        """
        loader_kwargs = loader_kwargs or {}
        
        # 根据glob模式推断文件类型
        if ".txt" in glob_pattern:
            loader_cls = TextLoader
        else:
            # 对于其他类型，使用UnifiedDocumentLoader
            unified = UnifiedDocumentLoader()
            return unified.load_directory(directory)
        
        loader = DirectoryLoader(
            directory,
            glob=glob_pattern,
            loader_cls=loader_cls,
            loader_kwargs=loader_kwargs,
            show_progress=True
        )
        
        return loader.load()


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 使用统一加载器
    loader = UnifiedDocumentLoader()
    docs = loader.load_directory("./data/docs")
    
    print(f"\n总共加载了 {len(docs)} 个文档块")
    
    # 统计各类型文件
    type_count = {}
    for doc in docs:
        file_type = doc.metadata.get("file_type", "unknown")
        type_count[file_type] = type_count.get(file_type, 0) + 1
    
    print("文件类型统计:")
    for file_type, count in type_count.items():
        print(f"  {file_type}: {count}")
