# FastAPI基础应用结构
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import time
from typing import Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理 - 启动和关闭时执行"""
    # 启动时执行
    logger.info("🚀 FastAPI应用启动中...")
    # 这里可以初始化数据库连接、加载AI模型等
    yield
    # 关闭时执行
    logger.info("👋 FastAPI应用关闭中...")

# 创建FastAPI应用实例
app = FastAPI(
    title="AI服务API",
    description="基于FastAPI的AI应用开发框架",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS中间件配置 - 允许跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求计时中间件 - 记录每个请求的处理时间
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """记录请求处理时间"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"请求 {request.url.path} 处理耗时: {process_time:.4f}秒")
    return response

# 全局异常处理 - 统一处理HTTP异常
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常统一处理"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.detail,
            "status_code": exc.status_code
        }
    )

# 全局异常处理 - 统一处理其他异常
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """全局异常捕获"""
    logger.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": True,
            "message": "服务器内部错误",
            "detail": str(exc)
        }
    )

# 基础路由 - 健康检查
@app.get("/", tags=["根路由"])
async def root():
    """根路由 - 健康检查"""
    return {
        "message": "FastAPI AI服务运行中",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "service": "fastapi-ai-service"}

# 路径参数示例 - 展示路径参数和查询参数的使用
@app.get("/items/{item_id}", tags=["示例"])
async def read_item(item_id: int, q: Optional[str] = None):
    """带路径参数和查询参数的端点"""
    return {"item_id": item_id, "query": q}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
