from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_anthropic import ChatAnthropic

# GPT-5.4配置
chat_model = ChatOpenAI(
    model="gpt-5.4",
    temperature=0.7,
    max_tokens=2048,
    streaming=True  # 启用流式
)

# Claude配置
claude_model = ChatAnthropic(
    model="claude-4-opus-20250514",
    temperature=0.5
)

# Embedding模型
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-small"
)
