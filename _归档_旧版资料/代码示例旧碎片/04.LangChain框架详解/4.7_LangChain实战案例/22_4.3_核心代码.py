"""
文档问答 Pipeline
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
import hashlib
import json

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from config import CHUNK_SIZE, CHUNK_OVERLAP, TOP_K


class DocumentQAPipeline:
    """文档问答 Pipeline"""
    
    def __init__(
        self,
        document_path: str,
        api_key: Optional[str] = None,
        model_name: str = "gpt-5.4-mini",
        embedding_model: str = "text-embedding-3-small",
    ):
        """
        初始化 Pipeline
        
        Args:
            document_path: 文档路径
            api_key: API 密钥
            model_name: 模型名称
            embedding_model: 嵌入模型
        """
        self.document_path = Path(document_path)
        self.model_name = model_name
        self.embedding_model = embedding_model
        
        # 初始化 LLM 和嵌入
        self.llm = ChatOpenAI(model=model_name, api_key=api_key)
        self.embeddings = OpenAIEmbeddings(
            model=embedding_model,
            api_key=api_key,
        )
        
        # 文档处理
        self.documents: List[Document] = []
        self.vector_store = None
        self.qa_chain = None
        
        # 加载和索引文档
        self._load_and_index()
    
    def _load_and_index(self):
        """加载和索引文档"""
        # 根据文件类型选择加载方式
        suffix = self.document_path.suffix.lower()
        
        if suffix == ".pdf":
            self._load_pdf()
        elif suffix == ".docx":
            self._load_docx()
        elif suffix == ".md":
            self._load_markdown()
        elif suffix == ".txt":
            self._load_text()
        else:
            raise ValueError(f"不支持的文件类型: {suffix}")
        
        # 分割文档
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )
        splits = text_splitter.split_documents(self.documents)
        
        # 创建向量存储
        self.vector_store = Chroma.from_documents(
            documents=splits,
            embedding=self.embeddings,
        )
        
        # 创建检索器与 RAG 链（LCEL，v1.x 推荐方式）
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": TOP_K})
        qa_prompt = ChatPromptTemplate.from_template(
            "基于以下上下文回答问题。\n\n上下文：\n{context}\n\n问题：{question}"
        )
        self.qa_chain = (
            {
                "context": self.retriever | RunnableLambda(
                    lambda docs: "\n\n".join(d.page_content for d in docs)
                ),
                "question": RunnablePassthrough(),
            }
            | qa_prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _load_pdf(self):
        """加载 PDF"""
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(str(self.document_path))
        self.documents = loader.load()
    
    def _load_docx(self):
        """加载 Word 文档"""
        from langchain_community.document_loaders import Docx2txtLoader
        loader = Docx2txtLoader(str(self.document_path))
        self.documents = loader.load()
    
    def _load_markdown(self):
        """加载 Markdown"""
        from langchain_community.document_loaders import UnstructuredMarkdownLoader
        loader = UnstructuredMarkdownLoader(str(self.document_path))
        self.documents = loader.load()
    
    def _load_text(self):
        """加载文本文件"""
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(str(self.document_path), encoding="utf-8")
        self.documents = loader.load()
    
    def ask(self, question: str) -> Dict[str, Any]:
        """
        提问
        
        Args:
            question: 问题
            
        Returns:
            答案和来源
        """
        docs = self.retriever.invoke(question)
        answer = self.qa_chain.invoke(question)
        
        return {
            "question": question,
            "answer": answer,
            "source_documents": [
                {
                    "content": doc.page_content[:200] + "...",
                    "source": doc.metadata.get("source", "未知"),
                }
                for doc in docs
            ],
        }
    
    def batch_ask(self, questions: List[str]) -> List[Dict[str, Any]]:
        """批量提问"""
        return [self.ask(q) for q in questions]


# 使用示例
if __name__ == "__main__":
    # 创建 Pipeline
    pipeline = DocumentQAPipeline(
        document_path="./data/docs/manual.md",
    )
    
    # 提问
    result = pipeline.ask("这份文档的主要内容是什么？")
    
    print(f"问题: {result['question']}")
    print(f"答案: {result['answer']}")
    print(f"来源数量: {len(result['source_documents'])}")
