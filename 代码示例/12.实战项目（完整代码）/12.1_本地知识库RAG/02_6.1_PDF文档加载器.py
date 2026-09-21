# src/loaders/pdf_loader.py
# PDF文档加载器
from typing import List
from pathlib import Path
from langchain_community.document_loaders import (
    PyPDFLoader,           # 基础PDF加载器
    PyMuPDFLoader,         # 使用PyMuPDF的加载器，性能更好
    PDFPlumberLoader       # 使用PDFPlumber的加载器
)
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class PDFDocumentLoader:
    """PDF文档加载器
    
    支持多种PDF加载方式，可以根据需求选择
    - PyPDFLoader: 基础实现，兼容性较好
    - PyMuPDFLoader: 性能更好，支持更多PDF特性
    - PDFPlumberLoader: 表格提取能力强
    """
    
    def __init__(self, loader_type: str = "pymupdf"):
        """
        参数:
            loader_type: 加载器类型，可选 "pypdf", "pymupdf", "pdfplumber"
        """
        self.loader_type = loader_type.lower()
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """加载单个PDF文件
        
        参数:
            file_path: PDF文件路径
        返回:
            Document对象列表
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {file_path}")
        
        logger.info(f"开始加载PDF文件: {file_path}")
        
        # 根据类型选择加载器
        if self.loader_type == "pypdf":
            loader = PyPDFLoader(file_path)
        elif self.loader_type == "pdfplumber":
            loader = PDFPlumberLoader(file_path)
        else:  # pymupdf (default)
            loader = PyMuPDFLoader(file_path)
        
        # 加载文档
        documents = loader.load()
        
        # 添加元数据
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_type"] = "pdf"
            doc.metadata["file_name"] = path.name
        
        logger.info(f"PDF文件加载完成，共 {len(documents)} 页")
        return documents
    
    def load_pdfs_from_directory(self, directory: str) -> List[Document]:
        """从目录加载所有PDF文件
        
        参数:
            directory: 目录路径
        返回:
            所有PDF的Document列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        all_documents = []
        
        # 递归查找所有PDF文件
        pdf_files = list(dir_path.rglob("*.pdf"))
        
        logger.info(f"找到 {len(pdf_files)} 个PDF文件")
        
        for pdf_file in pdf_files:
            try:
                documents = self.load_pdf(str(pdf_file))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"加载PDF失败 {pdf_file}: {e}")
        
        return all_documents


class PDFWithOCRLoader:
    """支持OCR的PDF加载器
    
    用于处理扫描版PDF或图片型PDF
    需要安装 paddlepaddle 和 paddleocr
    """
    
    def __init__(self):
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(use_angle_cls=True, lang='ch')
            self.ocr_available = True
        except ImportError:
            logger.warning("PaddleOCR未安装，将使用基础加载器")
            self.ocr_available = False
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """使用OCR加载PDF
        
        参数:
            file_path: PDF文件路径
        返回:
            Document对象列表
        """
        if not self.ocr_available:
            # 回退到基础加载器
            loader = PyMuPDFLoader(file_path)
            return loader.load()
        
        # 使用OCR处理PDF
        # 这里需要将PDF页面转换为图像，然后用OCR识别
        # 实际实现较为复杂，这里提供基础框架
        raise NotImplementedError("OCR加载器需要额外配置")


# 使用示例
if __name__ == "__main__":
    # 配置日志
    logging.basicConfig(level=logging.INFO)
    
    # 加载单个PDF
    loader = PDFDocumentLoader(loader_type="pymupdf")
    docs = loader.load_pdf("./data/docs/pdf/sample.pdf")
    
    print(f"加载了 {len(docs)} 页")
    for i, doc in enumerate(docs[:3]):  # 只打印前3页
        print(f"--- 第{i+1}页 ---")
        print(doc.page_content[:200])
