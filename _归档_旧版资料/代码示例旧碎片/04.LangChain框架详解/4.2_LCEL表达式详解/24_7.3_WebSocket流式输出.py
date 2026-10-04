import json
"""
WebSocket流式输出示例
完整的前后端集成方案
"""

# 后端 FastAPI + WebSocket
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI()

llm = ChatOpenAI(streaming=True)
chain = ChatPromptTemplate.from_template("{message}") | llm

class WebSocketCallback:
    def __init__(self, websocket: WebSocket):
        self.websocket = websocket
    
    async def on_llm_new_token(self, token: str, **kwargs):
        await self.websocket.send_text(token)

@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            # 接收用户消息
            data = await websocket.receive_text()
            message = json.loads(data)["message"]
            
            # 使用回调发送流式响应
            callback = WebSocketCallback(websocket)
            llm.callbacks = [callback]
            
            async for chunk in chain.astream({"message": message}):
                pass  # 回调会自动发送
    
    except WebSocketDisconnect:
        print("Client disconnected")
"""

# 前端 JavaScript
"""
const ws = new WebSocket('ws://localhost:8000/ws/chat');

ws.onmessage = (event) => {
    // 实时追加收到的token
    document.getElementById('response').innerHTML += event.data;
};

function sendMessage() {
    const message = document.getElementById('input').value;
    ws.send(JSON.stringify({ message }));
}
"""

print("WebSocket流式输出需要配合前端代码使用")
print("参见上述代码示例进行完整实现")
