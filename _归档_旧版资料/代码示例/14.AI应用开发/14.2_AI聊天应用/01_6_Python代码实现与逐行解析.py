from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from typing import Dict, List
import json
import uuid
import openai
import asyncio
from datetime import datetime

app = FastAPI()

# 存储活跃连接
class ConnectionManager:
    """WebSocket连接管理器"""
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str):
        """建立连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.user_sessions[client_id] = {
            "messages": [],
            "connected_at": datetime.now().isoformat()
        }
        print(f"[WebSocket] 用户 {client_id} 已连接")
    
    def disconnect(self, client_id: str):
        """断开连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.user_sessions:
            del self.user_sessions[client_id]
        print(f"[WebSocket] 用户 {client_id} 已断开")
    
    async def send_message(self, client_id: str, message: dict):
        """发送消息"""
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)
    
    async def broadcast(self, message: dict):
        """广播消息"""
        for client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

manager = ConnectionManager()

# WebSocket聊天端点
@app.websocket("/ws/chat/{client_id}")
async def websocket_chat(websocket: WebSocket, client_id: str):
    """WebSocket聊天连接"""
    await manager.connect(websocket, client_id)
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # 处理消息
            await handle_chat_message(client_id, message)
            
    except WebSocketDisconnect:
        manager.disconnect(client_id)

async def handle_chat_message(client_id: str, message: dict):
    """处理聊天消息"""
    msg_type = message.get("type", "text")
    content = message.get("content", "")
    
    # 保存用户消息
    session = manager.user_sessions[client_id]
    session["messages"].append({
        "role": "user",
        "content": content,
        "timestamp": datetime.now().isoformat()
    })
    
    # 发送"正在输入"状态
    await manager.send_message(client_id, {
        "type": "status",
        "status": "typing"
    })
    
    # 调用AI生成回复（流式）
    if msg_type == "text":
        await stream_chat_response(client_id, content)

async def stream_chat_response(client_id: str, user_message: str):
    """流式生成聊天回复"""
    client = openai.OpenAI()
    
    # 构建消息历史 - 最近5轮对话
    session = manager.user_sessions[client_id]
    messages = [
        {"role": "system", "content": "你是一个 helpful AI助手"}
    ] + [
        {"role": m["role"], "content": m["content"]}
        for m in session["messages"][-5:]
    ]
    
    # 创建流式响应
    stream = client.chat.completions.create(
        model="gpt-5.4-mini",
        messages=messages,
        stream=True,
        temperature=0.7
    )
    
    full_response = ""
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            token = chunk.choices[0].delta.content
            full_response += token
            
            # 发送token到客户端
            await manager.send_message(client_id, {
                "type": "stream",
                "token": token,
                "finished": False
            })
            
            await asyncio.sleep(0.01)  # 控制流式速度
    
    # 发送完成信号
    await manager.send_message(client_id, {
        "type": "stream",
        "token": "",
        "finished": True
    })
    
    # 保存AI回复
    session["messages"].append({
        "role": "assistant",
        "content": full_response,
        "timestamp": datetime.now().isoformat()
    })
    
    # 发送完整消息确认
    await manager.send_message(client_id, {
        "type": "complete",
        "content": full_response,
        "timestamp": datetime.now().isoformat()
    })


# 会话管理器
class SessionManager:
    """会话管理器（支持Redis持久化）"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.ttl = 3600 * 24  # 24小时过期
    
    def create_session(self, user_id: str) -> str:
        """创建新会话"""
        import hashlib
        session_id = hashlib.md5(f"{user_id}_{datetime.now()}".encode()).hexdigest()[:12]
        return session_id
    
    def add_message(self, session_id: str, role: str, content: str):
        """添加消息到会话"""
        # 实际实现需要存储到Redis或数据库
        pass
    
    def get_chat_history(self, session_id: str, limit: int = 10) -> List[Dict]:
        """获取聊天历史"""
        return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
