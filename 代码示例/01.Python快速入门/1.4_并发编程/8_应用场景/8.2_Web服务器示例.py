# FastAPI + asyncio（高并发Web服务器）
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/")
async def root():
    await asyncio.sleep(0.1)  # 模拟IO
    return {"message": "Hello"}
