"""
多 Agent 系统主应用
提供统一的执行接口
"""
import logging
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

from config import LLM_MODEL
from src.coordinator import AgentCoordinator

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# 初始化 FastAPI
app = FastAPI(
    title="多 Agent 协作系统",
    description="基于 LangChain 的多 Agent 协作系统",
    version="1.0.0",
)

# 全局变量
coordinator: Optional[AgentCoordinator] = None


class TaskRequest(BaseModel):
    """任务请求"""
    task: str
    use_cache: bool = True


class TaskResponse(BaseModel):
    """任务响应"""
    status: str
    result: Dict[str, Any]
    agent_status: Dict[str, Any]


class StatusResponse(BaseModel):
    """状态响应"""
    status: str
    agents: Dict[str, Any]


@app.on_event("startup")
async def startup_event():
    """应用启动初始化"""
    global coordinator
    logger.info("初始化多 Agent 系统...")
    coordinator = AgentCoordinator(model_name=LLM_MODEL)
    logger.info("多 Agent 系统初始化完成")


@app.post("/execute", response_model=TaskResponse)
async def execute_task(request: TaskRequest):
    """执行任务"""
    global coordinator
    
    if coordinator is None:
        raise HTTPException(status_code=500, detail="系统未初始化")
    
    try:
        logger.info(f"执行任务: {request.task}")
        result = coordinator.execute_task(request.task)
        
        return TaskResponse(
            status="success",
            result=result,
            agent_status=coordinator.get_agent_status(),
        )
    except Exception as e:
        logger.error(f"任务执行失败: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=StatusResponse)
async def get_status():
    """获取系统状态"""
    global coordinator
    
    if coordinator is None:
        raise HTTPException(status_code=500, detail="系统未初始化")
    
    return StatusResponse(
        status="running",
        agents=coordinator.get_agent_status(),
    )


@app.post("/reset")
async def reset_system():
    """重置系统"""
    global coordinator
    
    if coordinator is None:
        raise HTTPException(status_code=500, detail="系统未初始化")
    
    coordinator.reset()
    
    return {"status": "success", "message": "系统已重置"}


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
