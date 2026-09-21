# 1. OpenAI API
import openai

openai.api_key = "your-api-key"

response = openai.chat.completions.create(
    model="gpt-5.4",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "用Python写一个快速排序"}
    ]
)
print(response.choices[0].message.content)

# 2. LangChain - LLM 应用框架
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.4")
prompt = ChatPromptTemplate.from_template(
    "用中文解释什么是{topic}"
)
chain = prompt | llm
result = chain.invoke({"topic": "机器学习"})
print(result.content)

# 3. RAG (Retrieval Augmented Generation)
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA  # 旧版API，建议新项目使用LCEL

# 文档处理
text_splitter = CharacterTextSplitter(chunk_size=1000)
docs = text_splitter.split_text(long_text)

# 向量化存储
vectorstore = Chroma.from_texts(docs, OpenAIEmbeddings())

# 问答链
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 问答
result = qa.run("文档中关于什么内容？")

# 4. Agent 开发
from langchain.agents import create_agent
from langchain.tools import tool

@tool
def search_wikipedia(query: str) -> str:
    """搜索维基百科"""
    return f"{query}的搜索结果..."

tools = [search_wikipedia]

agent = create_agent(
    "gpt-5.4",
    tools=tools,
    system_prompt="你是一个有用的AI助手，可以使用工具帮助用户解决问题。"
)

result = agent.invoke({"input": "Python编程语言的创始人是谁？"})
