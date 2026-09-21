# config/config.py
# 配置管理模块
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """RAG系统配置类
    
    集中管理所有配置项，便于修改和维护
    支持从环境变量读取敏感信息
    """
    
    # ==================== 基础路径配置 ====================
    # 项目根目录
    BASE_DIR = Path(__file__).parent.parent
    
    # 数据目录
    DATA_DIR = BASE_DIR / "data"
    DOCS_DIR = DATA_DIR / "docs"
    PROCESSED_DIR = DATA_DIR / "processed"
    
    # 向量存储路径
    VECTOR_STORE_DIR = PROCESSED_DIR / "vectorstores"
    FAISS_INDEX_PATH = VECTOR_STORE_DIR / "faiss_index"
    CHROMA_DB_PATH = VECTOR_STORE_DIR / "chroma_db"
    
    # 模型目录
    MODELS_DIR = BASE_DIR / "models"
    
    # 日志目录
    LOGS_DIR = BASE_DIR / "logs"
    
    # ==================== LLM配置 ====================
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL: Optional[str] = os.getenv("OPENAI_BASE_URL")
    OPENAI_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-5.4-mini")
    OPENAI_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0"))
    
    # 可以切换为本地LLM（如Ollama）
    USE_LOCAL_LLM: bool = os.getenv("USE_LOCAL_LLM", "false").lower() == "true"
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.3")
    
    # ==================== Embeddings配置 ====================
    # 嵌入模型选择: openai, sentence-transformers, bge
    EMBEDDING_MODEL_PROVIDER: str = os.getenv("EMBEDDING_MODEL_PROVIDER", "openai")
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-3-small")
    
    # 本地嵌入模型配置（使用sentence-transformers）
    SENTENCE_TRANSFORMERS_MODEL: str = os.getenv("SENTENCE_TRANSFORMERS_MODEL", "paraphrase-multilingual-MiniLM-L12-v2")
    
    # BGE嵌入模型配置
    BGE_MODEL_NAME: str = os.getenv("BGE_MODEL_NAME", "BAAI/bge-small-zh-v1.5")
    
    # ==================== 向量数据库配置 ====================
    # 选择向量数据库: faiss, chroma
    VECTOR_STORE_TYPE: str = os.getenv("VECTOR_STORE_TYPE", "faiss")
    
    # FAISS索引类型: Flat, IVF, HNSW等
    FAISS_INDEX_TYPE: str = os.getenv("FAISS_INDEX_TYPE", "Flat")
    
    # ==================== 分块配置 ====================
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    
    # 按句子分割配置
    SENTENCE_SPLITTER_SEPARATOR: str = os.getenv("SENTENCE_SPLITTER_SEPARATOR", "\n")
    
    # ==================== 检索配置 ====================
    DEFAULT_TOP_K: int = int(os.getenv("DEFAULT_TOP_K", "3"))
    ENABLE_RERANKING: bool = os.getenv("ENABLE_RERANKING", "false").lower() == "true"
    RERANK_TOP_N: int = int(os.getenv("RERANK_TOP_N", "3"))
    
    # ==================== 查询重写配置 ====================
    ENABLE_QUERY_REWRITE: bool = os.getenv("ENABLE_QUERY_REWRITE", "false").lower() == "true"
    
    # ==================== Streamlit配置 ====================
    STREAMLIT_PORT: int = int(os.getenv("STREAMLIT_PORT", "8501"))
    STREAMLIT_SERVER_HEADLESS: bool = os.getenv("STREAMLIT_SERVER_HEADLESS", "true").lower() == "true"
    
    @classmethod
    def init_dirs(cls):
        """初始化所有必要的目录
        
        在系统启动时调用，确保所有目录都存在
        """
        for dir_path in [cls.DATA_DIR, cls.DOCS_DIR, cls.PROCESSED_DIR,
                         cls.VECTOR_STORE_DIR, cls.MODELS_DIR, cls.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # 创建子目录
        (cls.DOCS_DIR / "pdf").mkdir(exist_ok=True)
        (cls.DOCS_DIR / "word").mkdir(exist_ok=True)
        (cls.DOCS_DIR / "markdown").mkdir(exist_ok=True)

# 创建配置实例
config = Config()

if __name__ == "__main__":
    # 初始化目录
    config.init_dirs()
    print("配置初始化完成")
    print(f"文档目录: {config.DOCS_DIR}")
    print(f"向量存储目录: {config.VECTOR_STORE_DIR}")
