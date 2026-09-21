# src/chunking/semantic_splitter.py
# 语义分割器
from typing import List, Optional, Dict
from langchain_core.documents import Document
from langchain_text_splitters import MarkdownHeaderTextSplitter
import logging

logger = logging.getLogger(__name__)

class SemanticChunker:
    """语义分割器
    
    根据语义相似性进行分割
    适用于有明确主题边界的文档
    """
    
    def __init__(
        self,
        embedder=None,
        threshold: float = 0.5,
        min_chunk_size: int = 100,
        max_chunk_size: int = 1000
    ):
        """
        参数:
            embedder: 嵌入模型实例，用于计算语义相似度
            threshold: 语义相似度阈值，低于此值时分割
            min_chunk_size: 最小块大小
            max_chunk_size: 最大块大小
        """
        self.embedder = embedder
        self.threshold = threshold
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
    
    def split_documents(
        self,
        documents: List[Document],
        show_progress: bool = True
    ) -> List[Document]:
        """基于语义相似性分割文档
        
        步骤：
        1. 将文档分成句子
        2. 计算相邻句子间的语义相似度
        3. 在相似度低于阈值处分割
        
        参数:
            documents: 文档列表
            show_progress: 是否显示进度
        返回:
            分割后的文档列表
        """
        from .sentence_splitter import ChineseSentenceSplitter
        
        # 先用句子分割器分割
        sentence_splitter = ChineseSentenceSplitter(
            chunk_size=self.max_chunk_size,
            chunk_overlap=0
        )
        
        all_chunks = []
        
        for doc in tqdm(documents, disable=not show_progress):
            # 分割成句子
            sentences = sentence_splitter.split_text(doc.page_content)
            
            if not sentences:
                continue
            
            # 计算每个句子的嵌入
            if self.embedder:
                embeddings = self.embedder.embed_documents(sentences)
            else:
                # 没有embedder时使用简单的长度+关键词方法
                embeddings = None
            
            # 根据相似度分割
            chunks = self._create_chunks_by_similarity(
                sentences,
                embeddings,
                doc.metadata
            )
            
            all_chunks.extend(chunks)
        
        return all_chunks
    
    def _create_chunks_by_similarity(
        self,
        sentences: List[str],
        embeddings: Optional[List[List[float]]],
        metadata: Dict
    ) -> List[Document]:
        """根据相似度创建文本块"""
        import numpy as np
        from sklearn.metrics.pairwise import cosine_similarity
        
        if not embeddings or len(sentences) < 2:
            # 无法进行语义分割，回退到简单合并
            chunks = []
            current = ""
            for sent in sentences:
                if len(current) + len(sent) <= self.max_chunk_size:
                    current += sent + " "
                else:
                    if current:
                        chunks.append(Document(
                            page_content=current.strip(),
                            metadata={**metadata}
                        ))
                    current = sent + " "
            
            if current:
                chunks.append(Document(
                    page_content=current.strip(),
                    metadata={**metadata}
                ))
            
            return chunks
        
        # 计算相邻句子的相似度
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(
                [embeddings[i]],
                [embeddings[i + 1]]
            )[0][0]
            similarities.append(sim)
        
        # 根据阈值分割
        chunks = []
        current_chunk = ""
        
        for i, sent in enumerate(sentences):
            current_chunk += sent + " "
            
            # 检查是否应该分割
            should_split = (
                len(current_chunk) >= self.min_chunk_size and
                (i < len(similarities) and similarities[i] < self.threshold)
            ) or len(current_chunk) >= self.max_chunk_size
            
            if should_split:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={**metadata}
                ))
                current_chunk = ""
        
        # 添加最后一个块
        if current_chunk.strip():
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={**metadata}
            ))
        
        return chunks


class MarkdownHeaderSplitter:
    """Markdown标题分割器
    
    根据Markdown标题结构进行分割
    适用于有明确标题层级的文档
    """
    
    def __init__(
        self,
        headers_to_split_on: Optional[List[tuple]] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ):
        """
        参数:
            headers_to_split_on: 要分割的标题级别 [(#, "标题1"), (##, "标题2")]
            chunk_size: 最大块大小
            chunk_overlap: 重叠大小
        """
        if headers_to_split_on is None:
            # 默认分割所有级别标题
            headers_to_split_on = [
                ("#", "标题1"),
                ("##", "标题2"),
                ("###", "标题3"),
                ("####", "标题4")
            ]
        
        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            return_each_line=False
        )
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_text(self, text: str) -> List[str]:
        """按标题分割文本"""
        # 先按标题分割
        splits = self.splitter.split_text(text)
        
        # 后处理：合并过小的块
        chunks = []
        current = ""
        
        for split in splits:
            content = split.page_content
            
            if len(current) + len(content) <= self.chunk_size:
                current += content + "\n\n"
            else:
                if current:
                    chunks.append(current.strip())
                
                # 如果单个块就超过限制，强制分割
                if len(content) > self.chunk_size:
                    # 简单按字符分割
                    sub_chunks = [
                        content[i:i+self.chunk_size]
                        for i in range(0, len(content), self.chunk_size - self.chunk_overlap)
                    ]
                    chunks.extend(sub_chunks[:-1])
                    current = sub_chunks[-1] if sub_chunks else ""
                else:
                    current = content + "\n\n"
        
        if current:
            chunks.append(current.strip())
        
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割文档列表"""
        all_chunks = []
        
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "chunking_method": "markdown_header"
                    }
                ))
        
        return all_chunks


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # 测试Markdown标题分割器
    md_text = """
# 人工智能简介

人工智能是计算机科学的一个分支，致力于创建智能机器。

## 机器学习

机器学习是人工智能的核心，让计算机从数据中学习。

### 监督学习

监督学习使用标记数据进行训练。

### 无监督学习

无监督学习处理未标记的数据。

## 深度学习

深度学习使用多层神经网络学习数据的表示。
    """
    
    splitter = MarkdownHeaderSplitter()
    chunks = splitter.split_text(md_text)
    
    print(f"Markdown分割得到 {len(chunks)} 个块:\n")
    for i, chunk in enumerate(chunks):
        print(f"--- 块 {i+1} ---")
        print(chunk[:100])
        print()
