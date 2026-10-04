# src/retrieval/query_rewriter.py
# 查询重写模块
from typing import List, Optional, Dict
from langchain_core.documents import Document
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain.output_parsers import StrOutputParser
import logging

logger = logging.getLogger(__name__)


class QueryRewriter:
    """查询重写器
    
    在将用户查询发送给向量存储之前，先进行优化
    常见的重写策略：
    1. HyDE: 生成假设文档，用假设文档去检索
    2. Query Expansion: 扩展查询，加入相关术语
    3. Query Decomposition: 分解复杂查询为子查询
    """
    
    def __init__(self, llm=None):
        """
        参数:
            llm: 大语言模型实例
        """
        self.llm = llm or ChatOpenAI(temperature=0)
    
    def rewrite_simple(self, query: str) -> str:
        """简单查询重写
        
        清理和规范化查询文本
        
        参数:
            query: 原始查询
        返回:
            重写后的查询
        """
        # 去除多余空格
        query = " ".join(query.split())
        
        # 去除特殊字符（保留中文、英文、数字、常用标点）
        import re
        query = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:\'\"-]', '', query)
        
        return query.strip()
    
    def rewrite_hyde(self, query: str) -> str:
        """HyDE (Hypothetical Document Embeddings)
        
        让LLM生成一个假设的答案文档
        用这个假设文档去做检索，可以获得更好的效果
        
        参数:
            query: 用户查询
        返回:
            假设文档
        """
        hyde_prompt = PromptTemplate(
            template="请生成一个能够回答以下问题的理想文档。这个文档应该是详细、准确的，包含回答问题所需的关键信息。\n\n问题：{question}\n\n理想文档：",
            input_variables=["question"]
        )
        
        chain = hyde_prompt | self.llm | StrOutputParser()
        
        hypothetical_doc = chain.invoke({"question": query})
        
        logger.info(f"HyDE生成: {hypothetical_doc[:100]}...")
        
        return hypothetical_doc
    
    def rewrite_expand(self, query: str) -> str:
        """查询扩展
        
        添加与查询相关的术语和同义词
        
        参数:
            query: 用户查询
        返回:
            扩展后的查询
        """
        expand_prompt = PromptTemplate(
            template="请为以下查询添加3-5个相关搜索术语或同义词，以帮助更好地检索相关信息。\n只输出扩展后的查询，不要有其他解释。\n\n原始查询：{query}\n\n扩展后的查询：",
            input_variables=["query"]
        )
        
        chain = expand_prompt | self.llm | StrOutputParser()
        
        expanded_query = chain.invoke({"query": query})
        
        logger.info(f"查询扩展: {query} -> {expanded_query}")
        
        return expanded_query.strip()
    
    def rewrite_decompose(self, query: str) -> List[str]:
        """查询分解
        
        将复杂问题分解为多个简单问题
        
        参数:
            query: 复杂查询
        返回:
            子问题列表
        """
        decompose_prompt = PromptTemplate(
            template="请将以下复杂问题分解为2-4个简单的子问题。每个子问题应该能够独立检索相关信息。\n用换行分隔每个子问题。\n\n原始问题：{query}\n\n子问题：",
            input_variables=["query"]
        )
        
        chain = decompose_prompt | self.llm | StrOutputParser()
        
        sub_queries = chain.invoke({"query": query})
        
        # 解析子问题
        sub_queries = [q.strip() for q in sub_queries.split("\n") if q.strip()]
        
        logger.info(f"查询分解: {query} -> {sub_queries}")
        
        return sub_queries
    
    def rewrite_conversational(self, query: str, chat_history: List[tuple]) -> str:
        """对话式查询重写
        
        结合对话历史理解当前查询
        解析代词指代、隐含意图等
        
        参数:
            query: 当前查询
            chat_history: 对话历史 [(问题, 回答), ...]
        返回:
            重写后的独立查询
        """
        # 构建历史上下文
        history_text = ""
        for i, (q, a) in enumerate(chat_history[-3:]):  # 只取最近3轮
            history_text += f"Q{i+1}: {q}\nA{i+1}: {a[:100]}...\n"
        
        rewrite_prompt = PromptTemplate(
            template="""根据对话历史，重写当前问题使其能够独立理解。

对话历史：
{history}

当前问题：{query}

重写后的独立问题（只输出问题，不要有其他解释）：""",
            input_variables=["history", "query"]
        )
        
        chain = rewrite_prompt | self.llm | StrOutputParser()
        
        rewritten_query = chain.invoke({
            "history": history_text,
            "query": query
        })
        
        logger.info(f"查询重写: {query} -> {rewritten_query}")
        
        return rewritten_query.strip()


class MultiQueryRetriever:
    """多查询检索器
    
    生成多个查询版本，检索所有结果并合并去重
    可以提高检索的召回率
    """
    
    def __init__(self, retriever, llm=None, num_queries: int = 3):
        """
        参数:
            retriever: 基础检索器
            llm: 大语言模型
            num_queries: 生成的查询数量
        """
        self.retriever = retriever
        self.rewriter = QueryRewriter(llm)
        self.num_queries = num_queries
    
    def get_relevant_documents(self, query: str) -> List[Document]:
        """获取相关文档
        
        参数:
            query: 用户查询
        返回:
            相关文档列表（已去重）
        """
        # 生成多个查询
        queries = [query]
        
        # 添加扩展查询
        try:
            expanded = self.rewriter.rewrite_expand(query)
            queries.append(expanded)
        except Exception as e:
            logger.warning(f"查询扩展失败: {e}")
        
        # 添加分解后的子查询
        try:
            sub_queries = self.rewriter.rewrite_decompose(query)
            queries.extend(sub_queries[:2])  # 最多加2个子查询
        except Exception as e:
            logger.warning(f"查询分解失败: {e}")
        
        # 去重
        queries = list(set(queries))[:self.num_queries]
        
        logger.info(f"多查询检索，使用 {len(queries)} 个查询: {queries}")
        
        # 检索所有文档
        all_docs = []
        seen_contents = set()
        
        for q in queries:
            try:
                docs = self.retriever.get_relevant_documents(q)
                
                for doc in docs:
                    # 简单的去重（基于内容前100字符）
                    content_key = doc.page_content[:100]
                    if content_key not in seen_contents:
                        seen_contents.add(content_key)
                        all_docs.append(doc)
            except Exception as e:
                logger.warning(f"查询 '{q}' 检索失败: {e}")
        
        return all_docs


# 使用示例
if __name__ == "__main__":
    import os
    os.environ["OPENAI_API_KEY"] = "your-api-key"
    
    # 测试查询重写
    rewriter = QueryRewriter()
    
    # 简单重写
    print("简单重写:")
    print(rewriter.rewrite_simple("  什么是   人工   智能？  "))
    
    # HyDE重写
    print("\nHyDE重写:")
    hyde_result = rewriter.rewrite_hyde("什么是机器学习？")
    print(hyde_result[:200])
    
    # 查询扩展
    print("\n查询扩展:")
    expand_result = rewriter.rewrite_expand("深度学习")
    print(expand_result)
    
    # 查询分解
    print("\n查询分解:")
    decompose_result = rewriter.rewrite_decompose("人工智能和机器学习有什么区别？")
    for q in decompose_result:
        print(f"  - {q}")
