# src/loaders/markdown_loader.py
# Markdown文档加载器
from typing import List
from pathlib import Path
from langchain_community.document_loaders import (
    UnstructuredMarkdownLoader,  # Unstructured Markdown加载器
    MarkdownLoader               # 基础Markdown加载器
)
from langchain_core.documents import Document
import re
import logging

logger = logging.getLogger(__name__)

class MarkdownDocumentLoader:
    """Markdown文档加载器
    
    支持加载Markdown文件，可以选择不同的加载策略
    - UnstructuredMarkdownLoader: 保持更好的结构
    - MarkdownLoader: 简单加载
    - 自定义加载器: 提取标题层级等信息
    """
    
    def __init__(self, loader_type: str = "unstructured"):
        """
        参数:
            loader_type: 加载器类型，可选 "unstructured", "basic", "custom"
        """
        self.loader_type = loader_type.lower()
    
    def load_md(self, file_path: str) -> List[Document]:
        """加载单个Markdown文件
        
        参数:
            file_path: Markdown文件路径
        返回:
            Document对象列表
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Markdown文件不存在: {file_path}")
        
        if path.suffix.lower() not in [".md", ".markdown"]:
            raise ValueError(f"不支持的文件格式: {path.suffix}")
        
        logger.info(f"开始加载Markdown文件: {file_path}")
        
        if self.loader_type == "unstructured":
            loader = UnstructuredMarkdownLoader(file_path)
            documents = loader.load()
        elif self.loader_type == "custom":
            documents = self._custom_load(file_path)
        else:  # basic
            loader = MarkdownLoader(file_path)
            documents = loader.load()
        
        # 添加元数据
        for doc in documents:
            doc.metadata["source"] = str(file_path)
            doc.metadata["file_type"] = "markdown"
            doc.metadata["file_name"] = path.name
        
        logger.info(f"Markdown文件加载完成，共 {len(documents)} 个文档块")
        return documents
    
    def _custom_load(self, file_path: str) -> List[Document]:
        """自定义加载器，提取更丰富的元数据
        
        提取标题层级、代码块等信息
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        documents = []
        
        # 提取元数据（YAML front matter）
        metadata = {}
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                # 简单的YAML解析
                for line in yaml_content.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip()
                content = parts[2]
        
        # 按标题分割内容
        sections = self._split_by_headings(content)
        
        for i, section in enumerate(sections):
            doc = Document(
                page_content=section["content"],
                metadata={
                    **metadata,
                    "heading": section.get("heading", ""),
                    "level": section.get("level", 1),
                    "section_index": i
                }
            )
            documents.append(doc)
        
        return documents
    
    def _split_by_headings(self, content: str) -> List[dict]:
        """按标题分割Markdown内容
        
        返回包含标题级别和内容的字典列表
        """
        lines = content.split("\n")
        sections = []
        current_section = {"heading": "", "level": 1, "content": ""}
        
        heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        
        for line in lines:
            match = heading_pattern.match(line)
            if match:
                # 保存前一个section
                if current_section["content"].strip():
                    sections.append(current_section)
                
                # 开始新section
                level = len(match.group(1))
                heading = match.group(2).strip()
                current_section = {
                    "heading": heading,
                    "level": level,
                    "content": ""
                }
            else:
                current_section["content"] += line + "\n"
        
        # 添加最后一个section
        if current_section["content"].strip():
            sections.append(current_section)
        
        # 如果没有标题，整个内容作为一个section
        if not sections:
            sections.append({
                "heading": "",
                "level": 1,
                "content": content
            })
        
        return sections
    
    def load_markdowns_from_directory(self, directory: str) -> List[Document]:
        """从目录加载所有Markdown文件
        
        参数:
            directory: 目录路径
        返回:
            所有Markdown的Document列表
        """
        dir_path = Path(directory)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"目录不存在: {directory}")
        
        all_documents = []
        
        # 查找所有Markdown文件
        md_files = list(dir_path.rglob("*.md")) + list(dir_path.rglob("*.markdown"))
        
        logger.info(f"找到 {len(md_files)} 个Markdown文件")
        
        for md_file in md_files:
            try:
                documents = self.load_md(str(md_file))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"加载Markdown失败 {md_file}: {e}")
        
        return all_documents


class EnhancedMarkdownLoader:
    """增强型Markdown加载器
    
    保留更多结构信息，适合技术文档处理
    """
    
    def __init__(self):
        self.heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$')
        self.code_block_pattern = re.compile(r'^```(\w*)\n([\s\S]*?)```')
        self.link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    
    def load(self, file_path: str) -> List[Document]:
        """加载Markdown文件，保留代码块和链接信息
        
        参数:
            file_path: Markdown文件路径
        返回:
            Document列表，每个代码块或段落作为一个文档
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        path = Path(file_path)
        documents = []
        
        # 处理代码块
        code_blocks = self.code_block_pattern.findall(content)
        for i, (language, code) in enumerate(code_blocks):
            doc = Document(
                page_content=code,
                metadata={
                    "source": str(file_path),
                    "file_name": path.name,
                    "file_type": "markdown",
                    "type": "code_block",
                    "language": language,
                    "index": i
                }
            )
            documents.append(doc)
        
        # 处理非代码内容
        # 这里可以添加更多处理逻辑
        
        return documents


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 加载Markdown文档
    loader = MarkdownDocumentLoader(loader_type="unstructured")
    docs = loader.load_md("./data/docs/markdown/sample.md")
    
    print(f"加载了 {len(docs)} 个文档块")
    for i, doc in enumerate(docs[:3]):
        print(f"--- 文档块 {i+1} ---")
        print(f"元数据: {doc.metadata}")
        print(f"内容: {doc.page_content[:100]}...")
