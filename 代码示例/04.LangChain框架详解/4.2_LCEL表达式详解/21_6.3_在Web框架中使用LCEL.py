"""
在FastAPI中使用LCEL
构建异步LLM API服务
"""

from fastapi import FastAPI
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import asyncio

app = FastAPI()

# 创建LLM和链
llm = ChatOpenAI()
qa_chain = (
    ChatPromptTemplate.from_template(
        "你是一个有帮助的助手。请回答以下问题：\n\n问题：{question}"
    )
    | llm
    | StrOutputParser()
)

# 请求模型
class QuestionRequest(BaseModel):
    question: str
    stream: bool = False

# ============================================================
# 标准异步端点
# ============================================================

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """异步非流式回答"""
    result = await qa_chain.ainvoke({"question": request.question})
    return {"answer": result}

# ============================================================
# 流式异步端点
# ============================================================

@app.post("/ask/stream")
async def ask_question_stream(request: QuestionRequest):
    """异步流式回答，返回Server-Sent Events"""
    from fastapi.responses import StreamingResponse
    
    async def generate():
        async for chunk in qa_chain.astream({"question": request.question}):
            yield f"data: {chunk}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream"
    )

# ============================================================
# 批量异步端点
# ============================================================

class BatchRequest(BaseModel):
    questions: list[str]

@app.post("/ask/batch")
async def ask_batch(request: BatchRequest):
    """批量异步处理多个问题"""
    inputs = [{"question": q} for q in request.questions]
    results = await qa_chain.abatch(inputs)
    return {"answers": results}

"""
启动服务：
uvicorn main:app --reload

测试：
curl -X POST http://localhost:8000/ask \
     -H "Content-Type: application/json" \
     -d '{"question": "什么是LCEL？"}'

curl -X POST http://localhost:8000/ask/stream \
     -H "Content-Type: application/json" \
     -d '{"question": "什么是LCEL？", "stream": true}'
"""
