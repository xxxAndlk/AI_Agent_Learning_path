"""
RAG 系统主应用
提供 REST API 接口
"""
import logging
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from config import (
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    TOP_K,
    SIMILARITY_THRESHOLD,
    LLM_MODEL,
    EMBEDDING_MODEL,
    PERSIST_DIRECTORY,
)
from src.document_loader import DocumentLoader
from src.text_splitter import TextSplitter
from src.vector_store import VectorStoreManager
from src.retriever import AdvancedRetriever
from src.chain import RAGChain

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化 FastAPI
app = FastAPI(
    title="RAG 知识库问答系统",
    description="基于 LangChain 的企业知识库问答系统",
    version="1.0.0",
)

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
vector_store_manager: Optional[VectorStoreManager] = None
rag_chain: Optional[RAGChain] = None


class QueryRequest(BaseModel):
    """查询请求模型"""
    question: str
    k: Optional[int] = TOP_K
    use_compression: bool = False


class QueryResponse(BaseModel):
    """查询响应模型"""
    answer: str
    sources: list
    num_sources: int


class UploadResponse(BaseModel):
    """上传响应模型"""
    status: str
    message: str
    document_count: int


@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    global vector_store_manager, rag_chain
    
    logger.info("初始化 RAG 系统...")
    
    # 初始化向量存储管理器
    vector_store_manager = VectorStoreManager(
        persist_directory=PERSIST_DIRECTORY,
        embedding_model=EMBEDDING_MODEL,
    )
    vector_store_manager.initialize_embeddings()
    
    # 尝试加载已存在的向量存储
    vector_store = vector_store_manager.load_vector_store()
    
    if vector_store:
        # 创建检索器
        base_retriever = vector_store_manager.get_retriever(
            k=TOP_K,
            score_threshold=SIMILARITY_THRESHOLD,
        )
        retriever = AdvancedRetriever(base_retriever)
        
        # 创建 RAG 链
        rag_chain = RAGChain(
            retriever=retriever,
            model_name=LLM_MODEL,
        )
        
        logger.info("RAG 系统初始化完成（已加载历史数据）")
    else:
        logger.info("RAG 系统初始化完成（等待上传文档）")


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(
    files: list[UploadFile] = File(...),
):
    """上传文档接口"""
    global vector_store_manager, rag_chain
    
    if vector_store_manager is None:
        raise HTTPException(status_code=500, detail="系统未初始化")
    
    # 保存上传的文件
    save_dir = Path("./data/docs")
    save_dir.mkdir(parents=True, exist_ok=True)
    
    saved_files = []
    for file in files:
        file_path = save_dir / file.filename
        content = await file.read()
        file_path.write_bytes(content)
        saved_files.append(file_path)
        logger.info(f"保存文件: {file.filename}")
    
    # 加载文档
    loader = DocumentLoader()
    all_documents = []
    for file_path in saved_files:
        try:
            documents = loader.load_file(file_path)
            all_documents.extend(documents)
        except Exception as e:
            logger.error(f"加载文件失败 {file_path.name}: {str(e)}")
    
    # 分割文档
    splitter = TextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    splits = splitter.split_documents(all_documents)
    
    # 创建向量存储
    vector_store_manager.create_vector_store(splits)
    
    # 重建 RAG 链
    base_retriever = vector_store_manager.get_retriever(k=TOP_K)
    retriever = AdvancedRetriever(base_retriever)
    rag_chain = RAGChain(retriever=retriever, model_name=LLM_MODEL)
    
    return UploadResponse(
        status="success",
        message=f"成功处理 {len(splits)} 个文档块",
        document_count=len(splits),
    )


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """问答接口"""
    global rag_chain
    
    if rag_chain is None:
        raise HTTPException(
            status_code=400, 
            detail="请先上传文档或等待系统初始化完成"
        )
    
    try:
        result = rag_chain.get_answer_with_sources(request.question)
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"],
            num_sources=result["num_sources"],
        )
    except Exception as e:
        logger.error(f"查询失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
