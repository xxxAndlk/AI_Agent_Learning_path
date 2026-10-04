"""
基于LangChain的完整RAG系统实现
包含文档加载、分割、向量化、检索、生成全流程
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# ============================================================
# 步骤1：加载文档
# ============================================================
# TextLoader用于加载纯文本文件
# 支持多种编码，自动处理文件IO
loader = TextLoader("./data/document.txt", encoding="utf-8")
documents = loader.load()  # 返回Document对象列表
# Document结构：page_content(文本内容), metadata(元数据字典)

# ============================================================
# 步骤2：文档分割
# ============================================================
# RecursiveCharacterTextSplitter是推荐的分割器
# chunk_size: 每个块的目标字符数
# chunk_overlap: 相邻块的重叠字符数（保持上下文连贯）
# separators: 分割时优先尝试的分隔符列表
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "，", " ", ""]
)
chunks = splitter.split_documents(documents)
print(f"文档分割为 {len(chunks)} 个片段")

# ============================================================
# 步骤3：创建向量存储
# ============================================================
# OpenAIEmbeddings使用text-embedding-3-small模型（默认）
# 将文本转换为1536维向量
embeddings = OpenAIEmbeddings()

# FAISS是Facebook开源的高效向量相似度搜索库
# from_documents()自动完成：嵌入生成 + 索引构建
vector_store = FAISS.from_documents(chunks, embeddings)

# 保存索引到磁盘（可选）
vector_store.save_local("./faiss_index")

# ============================================================
# 步骤4：创建检索器
# ============================================================
# as_retriever()将VectorStore转换为Retriever接口
# search_kwargs控制检索行为：
#   - k: 返回最相似的k个文档
#   - score_threshold: 相似度阈值过滤
retriever = vector_store.as_retriever(
    search_type="similarity",  # 相似度搜索（默认）
    search_kwargs={"k": 4}     # 返回Top-4文档
)

# ============================================================
# 步骤5：定义RAG Prompt模板
# ============================================================
# {context}将由检索器自动填充
# {question}是用户的原始问题
rag_prompt = ChatPromptTemplate.from_template("""
基于以下上下文信息回答问题。如果上下文中没有相关信息，请说明无法回答。

上下文：
{context}

问题：{question}

请提供详细且准确的答案：
""")

# ============================================================
# 步骤6：创建格式化函数
# ============================================================
def format_docs(docs):
    """
    将检索到的文档列表格式化为字符串
    每个文档包含page_content和metadata
    """
    return "\n\n".join([
        f"[文档 {i+1}] {doc.page_content}"
        for i, doc in enumerate(docs)
    ])

# ============================================================
# 步骤7：使用LCEL构建RAG链
# ============================================================
# RunnablePassthrough()将输入原样传递，用于保持question字段
# retriever.invoke(question)检索相关文档
# format_docs将文档列表转为字符串作为context
# 最终输入到prompt模板：{context, question}
rag_chain = (
    {
        "context": retriever | format_docs,  # 检索并格式化文档
        "question": RunnablePassthrough()     # 保留原始问题
    }
    | rag_prompt    # 填充模板
    | llm           # 调用LLM
    | StrOutputParser()  # 解析输出
)

# ============================================================
# 步骤8：执行RAG查询
# ============================================================
question = "LangChain的主要特点是什么？"

# 同步调用
answer = rag_chain.invoke(question)
print(f"问题：{question}")
print(f"答案：{answer}")

# 查看检索到的文档（用于调试）
retrieved_docs = retriever.invoke(question)
print(f"\n检索到 {len(retrieved_docs)} 个相关片段")
for i, doc in enumerate(retrieved_docs, 1):
    print(f"{i}. {doc.page_content[:100]}...")
