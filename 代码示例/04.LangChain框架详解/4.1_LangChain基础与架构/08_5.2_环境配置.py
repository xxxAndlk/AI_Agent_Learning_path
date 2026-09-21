import os
from langsmith import Client

# OpenAI API Key
os.environ["OPENAI_API_KEY"] = "your-api-key"

# LangSmith配置（用于追踪）
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-langsmith-key"
os.environ["LANGCHAIN_PROJECT"] = "my-project"
