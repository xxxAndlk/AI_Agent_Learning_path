"""
完整RAG链实现示例
包含从文档加载到问答的完整流程
"""

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os

# ============================================================
# 步骤1：配置API密钥
# ============================================================
os.environ["OPENAI_API_KEY"] = "your-api-key"

# ============================================================
# 步骤2：初始化模型和嵌入
# ============================================================

# LLM用于生成答案
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.3
)

# 嵌入模型用于将文本转换为向量
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)

# ============================================================
# 步骤3：文档处理（一次性准备）
# ============================================================

# 加载文档
loader = TextLoader("./data/knowledge.txt", encoding="utf-8")
documents = loader.load()

# 分割文档为小块
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", "，", " ", ""]
)
chunks = splitter.split_documents(documents)
print(f"文档已分割为 {len(chunks)} 个片段")

# 创建向量存储
vector_store = FAISS.from_documents(chunks, embeddings)
print("向量存储已创建")

# 保存到磁盘（可选）
vector_store.save_local("./faiss_index")

# 加载已有索引（可选）
# vector_store = FAISS.load_local("./faiss_index", embeddings)

# ============================================================
# 步骤4：创建检索器
# ============================================================

# 配置检索器
retriever = vector_store.as_retriever(
    search_type="similarity",  # 相似度搜索
    search_kwargs={"k": 4}    # 返回Top-4结果
)

# 测试检索
test_docs = retriever.invoke("LangChain的核心特性是什么？")
print(f"检索到 {len(test_docs)} 个相关文档")

# ============================================================
# 步骤5：构建RAG链
# ============================================================

# 定义格式化函数，将检索到的文档合并为上下文
def format_docs(docs):
    """将文档列表格式化为字符串"""
    return "\n\n".join([
        f"文档 {i+1}:\n{doc.page_content}"
        for i, doc in enumerate(docs)
    ])

# 定义RAG提示模板
rag_prompt = ChatPromptTemplate.from_template("""
你是一个专业的知识库问答助手。基于以下提供的上下文信息回答用户的问题。

要求：
1. 只根据提供的上下文回答，不要编造信息
2. 如果上下文中没有相关信息，请明确说明
3. 回答要清晰、准确、完整

上下文信息：
{context}

用户问题：{question}

请给出详细的回答：
""")

# 构建完整的RAG链
# 流程：用户输入 -> 检索文档 -> 格式化上下文 -> 填充Prompt -> LLM生成 -> 解析输出
rag_chain = (
    # 并行准备检索和保留原始问题
    {
        "context": retriever | format_docs,  # 检索并格式化文档
        "question": RunnablePassthrough()     # 保留原始问题
    }
    | rag_prompt    # 填充Prompt模板
    | llm           # 调用LLM生成答案
    | StrOutputParser()  # 解析输出为字符串
)

# ============================================================
# 步骤6：执行RAG查询
# ============================================================

# 提出问题
question = "LangChain的核心特性有哪些？"

print(f"\n问题：{question}")
print("-" * 50)

# 同步调用
answer = rag_chain.invoke(question)
print(f"答案：{answer}")

# 流式调用（更好的用户体验）
print("\n流式输出：")
for chunk in rag_chain.stream(question):
    print(chunk, end="", flush=True)
print()
