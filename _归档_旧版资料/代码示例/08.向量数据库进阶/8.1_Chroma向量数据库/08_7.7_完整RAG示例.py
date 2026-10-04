"""
完整的RAG系统示例 - 结合Chroma和LLM
"""

from typing import List, Dict, Any, Optional
import chromadb
import json


class RAGSystem:
    """检索增强生成系统"""
    
    def __init__(
        self,
        persist_directory: str = "./rag_db",
        collection_name: str = "knowledge_base"
    ):
        self.client = chromadb.PersistentClient(
            path=persist_directory
        )
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            embedding_function=None  # 使用默认嵌入
        )
    
    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict],
        ids: Optional[List[str]] = None
    ):
        """添加文档到知识库"""
        if ids is None:
            ids = [f"doc_{i}" for i in range(len(documents))]
        
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        print(f"已添加 {len(documents)} 个文档")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """检索相关文档"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        
        retrieved_docs = []
        for i in range(len(results['ids'][0])):
            retrieved_docs.append({
                "id": results['ids'][0][i],
                "content": results['documents'][0][i],
                "metadata": results['metadatas'][0][i],
                "distance": results['distances'][0][i]
            })
        
        return retrieved_docs
    
    def generate_response(
        self,
        query: str,
        retrieved_docs: List[Dict]
    ) -> str:
        """
        生成回复
        实际项目中应该调用LLM API
        """
        # 模拟LLM生成
        context = "\n\n".join([
            f"[{doc['metadata'].get('source', 'unknown')}] {doc['content']}"
            for doc in retrieved_docs
        ])
        
        prompt = f"""基于以下参考资料回答问题：

问题: {query}

参考资料:
{context}

请根据参考资料生成回答："""
        
        # 这里应该调用真实的LLM
        return f"基于检索到的 {len(retrieved_docs)} 个参考资料，这是模拟的LLM回复..."
    
    def chat(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """完整的对话流程"""
        # 1. 检索
        retrieved_docs = self.retrieve(query, top_k)
        
        # 2. 生成
        response = self.generate_response(query, retrieved_docs)
        
        return {
            "query": query,
            "response": response,
            "retrieved_docs": retrieved_docs,
            "doc_count": len(retrieved_docs)
        }


def demo_rag():
    """RAG系统演示"""
    
    # 初始化系统
    rag = RAGSystem(
        persist_directory="./demo_rag",
        collection_name="company_kb"
    )
    
    # 添加知识库文档
    documents = [
        "公司年假政策：入职满1年享受5天年假，满3年享受10天，年假按自然年计算。",
        "报销流程：费用发生后30天内提交报销申请，需提供发票和付款凭证。",
        "加班规定：工作日加班按1.5倍工资计算，休息日加班按2倍，节假日按3倍。",
        "考勤制度：上下班需打卡，迟到早退3次扣除当月全勤奖。",
        "员工福利：五险一金、商业保险、年度体检、节日礼品。",
        "离职流程：提前30天提交辞职报告，办理工作交接，结清工资。"
    ]
    
    metadatas = [
        {"category": "HR", "source": "员工手册"},
        {"category": "财务", "source": "报销制度"},
        {"category": "HR", "source": "加班管理办法"},
        {"category": "HR", "source": "考勤制度"},
        {"category": "HR", "source": "福利政策"},
        {"category": "HR", "source": "离职管理办法"}
    ]
    
    rag.add_documents(documents, metadatas)
    
    # 测试查询
    queries = [
        "年假有多少天？",
        "报销需要什么材料？",
        "加班工资怎么计算？"
    ]
    
    for query in queries:
        result = rag.chat(query)
        print(f"\n问题: {query}")
        print(f"回答: {result['response']}")
        print(f"参考文档数: {result['doc_count']}")


if __name__ == "__main__":
    demo_rag()
