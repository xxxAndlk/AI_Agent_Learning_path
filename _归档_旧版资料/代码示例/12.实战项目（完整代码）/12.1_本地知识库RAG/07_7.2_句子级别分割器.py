# src/chunking/sentence_splitter.py
# 句子级别分割器
from typing import List, Optional
from langchain_text_splitters import (
    SentenceTransformersTokenTextSplitter,
    NLTKTextSplitter,
    SpacyTextSplitter
)
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

class SentenceTextSplitter:
    """句子级别文本分割器
    
    在句子边界处分割，适合需要完整句子的场景
    支持多种句子分割实现
    """
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        splitter_type: str = "nltk"
    ):
        """
        参数:
            chunk_size: 每个块的最大字符数
            chunk_overlap: 重叠字符数
            splitter_type: 分割器类型，可选 "nltk", "spacy", "token"
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter_type = splitter_type.lower()
        
        if self.splitter_type == "nltk":
            self._init_nltk_splitter()
        elif self.splitter_type == "spacy":
            self._init_spacy_splitter()
        elif self.splitter_type == "token":
            self._init_token_splitter()
        else:
            raise ValueError(f"不支持的分割器类型: {splitter_type}")
    
    def _init_nltk_splitter(self):
        """初始化NLTK分割器"""
        try:
            import nltk
            # 确保下载了punkt tokenizer
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                nltk.download('punkt')
            try:
                nltk.data.find('tokenizers/punkt_tab')
            except LookupError:
                nltk.download('punkt_tab')
            
            self.splitter = NLTKTextSplitter(chunk_size=self.chunk_size)
        except ImportError:
            logger.warning("NLTK未安装，回退到简单分割")
            self.splitter = None
    
    def _init_spacy_splitter(self):
        """初始化Spacy分割器"""
        try:
            import spacy
            # 加载中文或英文模型
            try:
                self.nlp = spacy.load("zh_core_web_sm")
            except OSError:
                self.nlp = spacy.load("en_core_web_sm")
            
            self.splitter = SpacyTextSplitter(
                chunk_size=self.chunk_size,
                separator="\n\n"
            )
        except ImportError:
            logger.warning("Spacy未安装，回退到NLTK")
            self._init_nltk_splitter()
    
    def _init_token_splitter(self):
        """初始化Token分割器"""
        self.splitter = SentenceTransformersTokenTextSplitter(
            chunk_size=self.chunk_size,
            tokens_per_chunk=self.chunk_size,
            overlap=self.chunk_overlap
        )
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割Document列表"""
        if self.splitter is None:
            # 回退到简单分割
            from .recursive_splitter import RecursiveTextSplitter
            fallback = RecursiveTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap
            )
            return fallback.split_documents(documents)
        
        chunks = []
        for doc in documents:
            if self.splitter_type == "token":
                # Token分割器直接处理文本
                texts = self.splitter.split_text(doc.page_content)
                for i, text in enumerate(texts):
                    chunks.append(Document(
                        page_content=text,
                        metadata={**doc.metadata, "chunk_index": i}
                    ))
            else:
                # NLTK和Spacy分割器
                texts = self.splitter.split_text(doc.page_content)
                for i, text in enumerate(texts):
                    chunks.append(Document(
                        page_content=text,
                        metadata={**doc.metadata, "chunk_index": i}
                    ))
        
        logger.info(f"句子分割完成，得到 {len(chunks)} 个块")
        return chunks


class ChineseSentenceSplitter:
    """中文句子分割器
    
    使用正则表达式进行中文分句
    适用于中文文档处理
    """
    
    import re
    
    # 中文标点符号
    CHINESE_PUNCTUATION = "。！？；"
    
    # 英文标点符号
    ENGLISH_PUNCTUATION = ".!?"
    
    # 分句正则
    SENTENCE_SPLIT_PATTERN = re.compile(
        f'([{CHINESE_PUNCTUATION}{ENGLISH_PUNCTUATION}])+\s*'
    )
    
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
    
    def split_sentences(self, text: str) -> List[str]:
        """将文本分割成句子
        
        参数:
            text: 输入文本
        返回:
            句子列表
        """
        # 使用正则分割
        sentences = self.SENTENCE_SPLIT_PATTERN.split(text)
        
        # 清理空句子
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def split_into_chunks(self, sentences: List[str]) -> List[str]:
        """将句子组合成块
        
        参数:
            sentences: 句子列表
        返回:
            文本块列表
        """
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # 如果加上这个句子不超过限制
            if len(current_chunk) + len(sentence) <= self.chunk_size:
                current_chunk += sentence + " "
            else:
                # 保存当前块
                if current_chunk:
                    chunks.append(current_chunk.strip())
                
                # 如果单个句子就超过限制，需要分割这个句子
                if len(sentence) > self.chunk_size:
                    # 递归处理超长句子
                    sub_chunks = self._split_long_sentence(sentence)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""
                else:
                    # 开始新块，保留重叠
                    if self.chunk_overlap > 0 and chunks:
                        # 取前一个块的最后部分作为重叠
                        prev_chunk = chunks[-1]
                        overlap_text = prev_chunk[-self.chunk_overlap:]
                        current_chunk = overlap_text + sentence + " "
                    else:
                        current_chunk = sentence + " "
        
        # 添加最后一个块
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """分割超长句子
        
        对于超过chunk_size的句子，按字符分割
        """
        chunks = []
        
        # 按单词或字符分割
        words = list(sentence)
        
        current = ""
        for word in words:
            if len(current) + 1 <= self.chunk_size:
                current += word
            else:
                chunks.append(current)
                current = word
        
        if current:
            chunks.append(current)
        
        return chunks
    
    def split_text(self, text: str) -> List[str]:
        """完整分割流程
        
        参数:
            text: 输入文本
        返回:
            文本块列表
        """
        sentences = self.split_sentences(text)
        chunks = self.split_into_chunks(sentences)
        return chunks
    
    def split_documents(self, documents: List[Document]) -> List[Document]:
        """分割Document列表"""
        all_chunks = []
        
        for doc in documents:
            chunks = self.split_text(doc.page_content)
            
            for i, chunk in enumerate(chunks):
                all_chunks.append(Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk_index": i,
                        "chunking_method": "chinese_sentence"
                    }
                ))
        
        return all_chunks


# 使用示例
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    test_text = """
    人工智能是计算机科学的一个分支，它试图理解智能的本质，并生产出一种新的能以人类智能相似的方式做出反应的智能机器。该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    
    机器学习是人工智能的核心，是使计算机具有智能的根本途径。它是一门多领域交叉学科，涉及概率论、统计学、逼近论、凸分析、算法复杂度理论等多门学科。机器学习专门研究计算机怎样模拟或实现人类的学习行为，以获取新的知识或技能，重新组织已有的知识结构使之不断改善自身的性能。
    
    深度学习是机器学习的分支，是一种以人工神经网络为架构，对数据进行表征学习的算法。深度学习在计算机视觉、语音识别、自然语言处理等领域取得了突破性进展。
    """
    
    # 使用中文句子分割器
    splitter = ChineseSentenceSplitter(chunk_size=200, chunk_overlap=30)
    chunks = splitter.split_text(test_text)
    
    print(f"分割得到 {len(chunks)} 个块:\n")
    for i, chunk in enumerate(chunks):
        print(f"--- 块 {i+1} ({len(chunk)} 字符) ---")
        print(chunk)
        print()
