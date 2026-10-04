import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import AsyncGenerator
import aiohttp


# 模拟AI模型推理
async def mock_ai_inference(prompt: str, model: str = "gpt-5.4-mini") -> str:
    """模拟AI模型推理（异步）"""
    # 模拟API调用延迟
    await asyncio.sleep(1.5)
    return f"AI回复: 基于'{prompt}'的思考 ({model})"


async def mock_embedding(text: str) -> list:
    """生成文本嵌入向量"""
    await asyncio.sleep(0.5)
    import random
    return [random.random() for _ in range(1536)]


# 路由中的异步处理
@api_router.post("/ai/chat")
async def chat(
    message: str = Body(..., embed=True),
    model: str = "gpt-5.4-mini"
):
    """AI对话接口（异步）"""
    result = await mock_ai_inference(message, model)
    return {"response": result, "model": model}


# 并发处理多个请求
@api_router.post("/ai/batch-chat")
async def batch_chat(messages: List[str], model: str = "gpt-5.4-mini"):
    """批量对话（并发处理）"""
    # 使用asyncio.gather并发执行多个AI请求
    tasks = [mock_ai_inference(msg, model) for msg in messages]
    results = await asyncio.gather(*tasks)
    
    return {
        "responses": results,
        "count": len(results),
        "model": model
    }


# 流式响应
from fastapi.responses import StreamingResponse
import json


async def generate_chunks():
    """生成流式响应数据"""
    for i in range(10):
        await asyncio.sleep(0.2)
        yield f"chunk {i}\n"


@api_router.get("/ai/stream")
async def ai_stream():
    """流式AI响应"""
    return StreamingResponse(
        generate_chunks(),
        media_type="text/event-stream"
    )


# 后台任务
from fastapi.background import BackgroundTasks


def write_log(message: str):
    """后台任务函数"""
    with open("log.txt", "a") as f:
        f.write(f"{message}\n")


@api_router.post("/ai/process")
async def process_ai_task(
    task_id: str,
    background_tasks: BackgroundTasks
):
    """后台AI处理任务"""
    # 立即返回，任务在后台执行
    background_tasks.add_task(write_log, f"处理任务: {task_id}")
    
    return {"message": "任务已提交", "task_id": task_id}


# 使用线程池执行CPU密集型任务
executor = ThreadPoolExecutor(max_workers=4)


def cpu_intensive_task(data: list) -> int:
    """CPU密集型任务"""
    # 模拟复杂计算
    result = 0
    for item in data:
        result += item ** 2
    return result


@api_router.post("/ai/compute")
async def compute(
    data: List[int]
):
    """计算密集型AI预处理"""
    # 将CPU密集型任务放到线程池执行，避免阻塞事件循环
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(executor, cpu_intensive_task, data)
    
    return {"result": result, "input_size": len(data)}


# 异步数据库操作（示例）
class AsyncDatabase:
    """异步数据库连接池"""
    
    def __init__(self):
        self.pool = None
    
    async def connect(self):
        """连接数据库"""
        # 实际使用 aiosqlite 或 asyncpg
        await asyncio.sleep(0.1)  # 模拟连接
        self.pool = "connected"
    
    async def disconnect(self):
        """断开连接"""
        await asyncio.sleep(0.1)
        self.pool = None
    
    async def query(self, sql: str):
        """异步查询"""
        await asyncio.sleep(0.1)  # 模拟查询
        return [{"id": 1, "name": "test"}]


# 应用启动和关闭时的数据库连接管理
db = AsyncDatabase()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    await db.connect()
    logger.info("数据库连接已建立")
    yield
    await db.disconnect()
    logger.info("数据库连接已关闭")


# 异步上下文依赖
async def get_db() -> AsyncGenerator[AsyncDatabase, None]:
    """获取数据库连接的依赖"""
    yield db


@api_router.get("/db/query")
async def query_db(db: AsyncDatabase = Depends(get_db)):
    """异步数据库查询"""
    results = await db.query("SELECT * FROM users")
    return results
