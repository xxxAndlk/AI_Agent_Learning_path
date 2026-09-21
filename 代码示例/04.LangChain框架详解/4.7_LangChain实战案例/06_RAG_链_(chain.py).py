"""
RAG 链模块
组合检索器和 LLM 生成答案
"""
import logging
from typing import Optional, List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document

from .retriever import AdvancedRetriever

logger = logging.getLogger(__name__)


class RAGChain:
    """RAG 链封装类"""
    
    def __init__(
        self,
        retriever: AdvancedRetriever,
        llm: Optional[ChatOpenAI] = None,
        model_name: str = "gpt-5.4-mini",
        temperature: float = 0.3,
        system_prompt: Optional[str] = None,
    ):
        """
        初始化 RAG 链
        
        Args:
            retriever: 检索器
            llm: LLM 模型
            model_name: 模型名称
            temperature: 温度参数
            system_prompt: 系统提示词
        """
        self.retriever = retriever
        self.llm = llm or ChatOpenAI(
            model=model_name,
            temperature=temperature,
        )
        
        # 默认系统提示词
        self.system_prompt = system_prompt or """你是一个专业的知识库问答助手。
请根据提供的上下文信息回答用户的问题。
如果上下文中没有相关信息，请明确告知用户你无法从知识库中找到答案。
请用清晰、准确的中文回答问题。"""
        
        # 初始化链
        self.chain = None
        self._build_chain()
    
    def _build_chain(self):
        """构建 RAG 链"""
        # 创建提示词模板
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "上下文信息:\n{context}\n\n用户问题: {question}"),
        ])
        
        # 格式化文档的函数
        def format_docs(docs: List[Document]) -> str:
            return "\n\n".join(
                f"[来源: {doc.metadata.get('source', '未知')}]\n{doc.page_content}"
                for doc in docs
            )
        
        # 构建链
        self.chain = (
            {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | self.llm
            | StrOutputParser()
        )
        
        logger.info("RAG 链构建完成")
    
    def invoke(self, query: str) -> str:
        """
        执行 RAG 链
        
        Args:
            query: 用户查询
            
        Returns:
            生成的答案
        """
        if self.chain is None:
            raise ValueError("RAG 链未初始化")
        
        logger.info(f"处理查询: {query}")
        
        try:
            result = self.chain.invoke(query)
            logger.info("查询处理完成")
            return result
        except Exception as e:
            logger.error(f"查询处理失败: {str(e)}")
            raise
    
    async def ainvoke(self, query: str) -> str:
        """异步执行 RAG 链"""
        if self.chain is None:
            raise ValueError("RAG 链未初始化")
        
        logger.info(f"异步处理查询: {query}")
        
        try:
            result = await self.chain.ainvoke(query)
            logger.info("异步查询处理完成")
            return result
        except Exception as e:
            logger.error(f"异步查询处理失败: {str(e)}")
            raise
    
    def get_answer_with_sources(
        self,
        query: str,
    ) -> Dict[str, Any]:
        """
        获取答案和来源信息
        
        Args:
            query: 用户查询
            
        Returns:
            包含答案和来源的字典
        """
        # 获取相关文档
        docs = self.retriever.search(query, k=5)
        
        # 格式化上下文
        context = "\n\n".join(doc.page_content for doc in docs)
        
        # 生成答案
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", "上下文信息:\n{context}\n\n用户问题: {question}"),
        ])
        
        chain = prompt | self.llm | StrOutputParser()
        answer = chain.invoke({"context": context, "question": query})
        
        # 提取来源
        sources = [
            {
                "source": doc.metadata.get("source", "未知"),
                "content": doc.page_content[:200] + "...",
            }
            for doc in docs
        ]
        
        return {
            "answer": answer,
            "sources": sources,
            "num_sources": len(sources),
        }
