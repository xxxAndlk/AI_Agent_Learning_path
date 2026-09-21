# src/loaders/word_loader.py
# Word文档加载器
from typing import List
from pathlib import Path
from langchain_community.document_loaders import (
    Docx2txtLoader,         # 加载Word文档文本
    UnstructuredWordLoader, # 使用Unstructured的加载器
    DocxLoader              # LangChain原生的Word加载器
)
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class WordDocumentLoader:
    """Word文档加载器
    
    支持加载 .docx 格式的Word文档
    不支持旧的 .doc 格式（需要转换为.docx）
    """
    
    def __init__(self, loader_type: str = "docx2txt"):
        """
        参数:
            loader_type: 加载器类型，可选 "docx2txt", "unstructured", "docx"
        """
        self.loader_type = loader_type.lower()
    
    def load_docx(self, file_path: str) -> List[Document]:
        """加载单个Word文档
        
        参数:
            file_path: Word文件路径
        返回:
            Document对象列表
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Word文件不存在: {file_path}")
        
        if path.suffix.lower() != ".docx":
            raise ValueError(f"不支持的文件格式: {path.suffix}，仅支持.docx")
        
        logger.info(f"开始加载Word文件: {file_path}")
        
        # 根据类型选择加载器
        if self.loader_type == "docx2txt":
            loader = Docx2txtLoader(file_path)
        elif self.loader_type == "unstructured":
            loader = UnstructuredWordLoader(file_path)
        else:
            loader = DocxLoader(file_path)
        
        # 加载文档
        documents = loader.load()
        
        # 添加元数据
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_type"] = "word"
            doc.metadata["file_name"] = path.name
        
        logger.info(f"Word文件加载完成，共 {len(documents)} 个文档块")
        return documents
    
    def load_docx_with_tables(self, file_path: str) -> List[Document]:
        """加载Word文档并保留表格
        
        使用Unstructured模式可以更好地处理表格
        """
        # 使用Unstructured模式，设置包含表格
        loader = UnstructuredWordLoader(
            file_path,
            mode="elements",  # 按元素分割，保留表格
            include_metadata=True
        )
        
        documents = loader.load()
        
        # 添加元数据
        path = Path(file_path)
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_type"] = "word"
            doc.metadata["file_name"] = path.name
        
        return documents
    
    def load_words_from_directory(self, directory: str) -> List[Document]:
        """从目录加载所有Word文件
        
        参数:
            directory: 目录路径
        返回:
            所有Word的Document列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        all_documents = []
        
        # 查找所有Word文件
        word_files = list(dir_path.rglob("*.docx"))
        
        logger.info(f"找到 {len(word_files)} 个Word文件")
        
        for word_file in word_files:
            try:
                documents = self.load_docx(str(word_file))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"加载Word失败 {word_file}: {e}")
        
        return all_documents


class LegacyWordLoader:
    """旧版Word格式加载器
    
    处理 .doc 格式（2003及以前）
    需要先转换为 .docx 格式
    """
    
    @staticmethod
    def convert_to_docx(doc_path: str, output_dir: str = None) -> str:
        """将旧版doc转换为docx格式
        
        使用LibreOffice或pandoc进行转换
        需要系统安装LibreOffice
        
        参数:
            doc_path: .doc文件路径
            output_dir: 输出目录，默认为同一目录
        返回:
            转换后的.docx文件路径
        """
        import subprocess
        import tempfile
        
        doc_path = Path(doc_path)
        
        if output_dir is None:
            output_dir = doc_path.parent
        else:
            output_dir = Path(output_dir)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 使用LibreOffice转换
        cmd = [
            "soffice",
            "--headless",
            "--convert-to", "docx",
            "--outdir", str(output_dir),
            str(doc_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            output_path = output_dir / f"{doc_path.stem}.docx"
            return str(output_path)
        except subprocess.CalledProcessError as e:
            logger.error(f"转换失败: {e}")
            raise


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 加载Word文档
    loader = WordDocumentLoader(loader_type="docx2txt")
    docs = loader.load_docx("./data/docs/word/sample.docx")
    
    print(f"加载了 {len(docs)} 个文档块")
    if docs:
        print(f"内容预览: {docs[0].page_content[:200]}")
