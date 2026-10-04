# -*- coding: utf-8 -*-
"""第02课配套：一个能在浏览器里真聊天的 AI 网页（连续对话 + 流式输出）。

零依赖段（默认运行）：纯标准库 http.server + 内嵌聊天页面，回复逐字推给浏览器。
真实框架段：FastAPI 版聊天接口对照，需先安装：pip install fastapi uvicorn

运行方式：
    python chat_app.py             # 浏览器打开 http://127.0.0.1:8766
    python chat_app.py --selftest  # 自动验证聊天接口（含流式分块）后退出
FastAPI 版启动：uvicorn chat_app:app --port 8766
"""
import io
import json
import shutil
import sys
import threading
import time
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 8766

PAGE = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>迷你 AI 聊天</title>
<style>body{font-family:sans-serif;max-width:560px;margin:30px auto;padding:0 16px}
#log{border:1px solid #ccc;border-radius:8px;height:320px;overflow-y:auto;padding:12px}
.msg{margin:6px 0;white-space:pre-wrap}.user{color:#0366d6}
#bar{margin-top:10px;display:flex;gap:8px}
input{flex:1;font-size:16px;padding:8px}button{font-size:16px;padding:8px 16px}</style>
</head><body>
<h2>迷你 AI 聊天（流式输出）</h2>
<div id="log"></div>
<div id="bar"><input id="t" placeholder="输入消息，回车或点发送" onkeydown="if(event.key==='Enter')send()">
<button onclick="send()">发送</button></div>
<script>
const log=document.getElementById('log'), t=document.getElementById('t');
const history=[];   // 连续对话的关键：历史在浏览器里攒着，每次随请求带给后端
function add(cls){const d=document.createElement('div');d.className='msg '+cls;log.appendChild(d);return d;}
async function send(){
  const text=t.value.trim(); if(!text)return; t.value='';
  history.push({role:'user',content:text}); add('user').textContent='你：'+text;
  const ai=add('ai'); ai.textContent='AI：';
  const r=await fetch('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({history:history,message:text})});
  const dec=new TextDecoder(); let out='';
  for await (const chunk of r.body){       // 逐块收流，边收边显示
    out+=dec.decode(chunk,{stream:true});
    ai.textContent='AI：'+out; log.scrollTop=log.scrollHeight;
  }
  history.push({role:'assistant',content:out});
}
</script></body></html>"""


def fake_reply(history: list, message: str) -> str:
    """假装 AI：按关键词回复，并体现"记得聊过几轮"。真实项目换成大模型流式 API。"""
    n = len([m for m in history if m.get("role") == "user"])
    low = message.lower()
    if "你好" in message or "hi" in low:
        head = "你好呀！随便聊两句试试，我的字是一个一个蹦出来的——这就是流式输出。"
    elif "名字" in message:
        head = "我是本课的迷你聊天机器人小π，暂时只会复读和客套。"
    elif "天气" in message:
        head = "天气我不知道，我只是课程里的假模型。但注意到了吗？这段话正在逐字到达你的屏幕。"
    elif "再见" in message or "拜拜" in message:
        head = "下次再聊！记得去看看 FastAPI 版的接口怎么写。"
    else:
        head = f"你说「{message}」，我先复读一下。真实项目里这一步会调用大模型 API。"
    return f"{head}（对了，这是你的第 {n} 条消息，之前的对话我还记得）"


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _body(self) -> dict:
        n = int(self.headers.get("Content-Length") or 0)
        parts, got = [], 0
        while got < n:
            part = self.rfile.read1(n - got)
            if not part:
                break
            parts.append(part)
            got += len(part)
        raw = b"".join(parts)
        return json.loads(raw) if raw.strip() else {}

    def do_GET(self):
        if self.path == "/":
            body = PAGE.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/chat":
            self.send_error(404)
            return
        data = self._body()
        reply = fake_reply(data.get("history", []), data.get("message", ""))
        # 流式输出的关键：不写 Content-Length，发完头部后逐字 write + flush
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Connection", "close")
        self.end_headers()
        for ch in reply:
            self.wfile.write(ch.encode("utf-8"))
            self.wfile.flush()
            time.sleep(0.03)


def serve():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"聊天服务已启动：http://127.0.0.1:{PORT}（按 Ctrl+C 停止）")
    return server


def _get(path: str) -> str:
    conn = HTTPConnection("127.0.0.1", PORT, timeout=5)
    conn.request("GET", path)
    resp = conn.getresponse()
    buf = io.BytesIO()
    shutil.copyfileobj(resp, buf)
    conn.close()
    return buf.getvalue().decode("utf-8")


def selftest():
    server = serve()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert "迷你 AI 聊天" in _get("/"), "聊天页 HTML 应可访问"
        conn = HTTPConnection("127.0.0.1", PORT, timeout=15)
        hist = [{"role": "user", "content": "你好"},
                {"role": "user", "content": "你叫什么名字"}]
        conn.request("POST", "/api/chat",
                     body=json.dumps({"history": hist, "message": "你叫什么名字"}).encode("utf-8"),
                     headers={"Content-Type": "application/json"})
        resp = conn.getresponse()
        assert resp.status == 200, f"聊天接口应返回 200，实际 {resp.status}"
        chunks, out = 0, ""
        while True:
            part = resp.read1(16)  # 一小口一小口拿，模拟浏览器收到流式分块
            if not part:
                break
            chunks += 1
            out += part.decode("utf-8")
        conn.close()
        assert "第 2 条消息" in out, f"应体现连续对话上下文，实际：{out[:60]}"
        assert chunks >= 5, f"流式应分多块到达，实际 {chunks} 块"
        print(f"selftest 通过：聊天页可访问，回复正常，响应分 {chunks} 块到达（流式生效）")
    finally:
        server.shutdown()
        server.server_close()
    print("服务已关闭")


# ---------- 对照：FastAPI 版聊天接口（pip install fastapi uvicorn） ----------
try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, StreamingResponse
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    print("（提示）未安装 FastAPI，真实框架段已跳过。想体验请先执行：pip install fastapi uvicorn")

if HAS_FASTAPI:
    app = FastAPI(title="迷你 AI 聊天")

    class ChatIn(BaseModel):
        history: list = []
        message: str

    @app.get("/")
    def home():
        return HTMLResponse(PAGE)

    @app.post("/api/chat")
    def chat(item: ChatIn):
        reply = fake_reply(item.history, item.message)

        def gen():
            for ch in reply:
                yield ch
                time.sleep(0.03)

        return StreamingResponse(gen(), media_type="text/plain; charset=utf-8")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        serve().serve_forever()
