"""
RAG 系统配置文件
定义所有可配置的参数
"""
import os
from typing import Literal

# OpenAI API 配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-api-key")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

# 模型配置
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5.4-mini")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")

# 向量存储配置
VECTOR_STORE_TYPE: Literal["chroma", "faiss", "milvus"] = "chroma"
PERSIST_DIRECTORY = os.getenv("PERSIST_DIRECTORY", "./storage/chroma")

# 文档处理配置
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "500"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "100"))

# 检索配置
TOP_K = int(os.getenv("TOP_K", "5"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.7"))

# 支持的文档类型
SUPPORTED_FILE_TYPES = [".txt", ".md", ".pdf", ".docx", ".html"]

# 应用配置
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
