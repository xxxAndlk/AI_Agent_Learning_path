# -*- coding: utf-8 -*-
"""第01课配套：把"模型调用"变成一个可访问的 API。

零依赖段（默认运行）：纯标准库 http.server 起一个真 API，浏览器打开就有页面。
真实框架段：FastAPI 写法对照，需先安装：pip install fastapi uvicorn（未装会中文提示并跳过）

运行方式：
    python fastapi_demo.py             # 起服务，浏览器打开 http://127.0.0.1:8765
    python fastapi_demo.py --selftest  # 自动起-请求-关闭，验证接口可用后退出
FastAPI 版启动：uvicorn fastapi_demo:app --reload   （新版也可：fastapi dev fastapi_demo.py）
"""
import io
import json
import shutil
import sys
import threading
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORT = 8765

# 前端页面：输入框 + 按钮，点击后由 JS 向后端接口发请求
PAGE = """<!DOCTYPE html>
<html lang="zh"><head><meta charset="utf-8"><title>AI 情绪分析 API</title>
<style>body{font-family:sans-serif;max-width:560px;margin:40px auto;padding:0 16px}
input,button{font-size:16px;padding:8px}button{cursor:pointer}
#out{margin-top:16px;padding:12px;border:1px solid #ccc;border-radius:8px;min-height:24px}</style>
</head><body>
<h2>AI 情绪分析 API</h2>
<p>前端负责展示，后端负责算：输入一句话点按钮，浏览器会把请求发给页面底部的接口。</p>
<p><input id="t" size="40" placeholder="比如：这家店的服务真棒">
<button onclick="go()">分析</button></p>
<div id="out">结果会出现在这里</div>
<hr><p>本页背后有三个接口：<code>GET /</code>（本页面）、<code>GET /api/health</code>、
<code>GET|POST /api/sentiment</code>。</p>
<script>
async function go(){
  const t=document.getElementById('t').value;
  const r=await fetch('/api/sentiment?q='+encodeURIComponent(t));
  const j=await r.json();
  document.getElementById('out').textContent='情绪：'+j.label+'（分数 '+j.score+'）';
}
</script></body></html>"""


def fake_model(text: str) -> dict:
    """假装这是一个 AI 模型：按关键词给情绪打分。真实项目里换成大模型调用。"""
    pos = ["好", "喜欢", "开心", "棒", "满意", "赞"]
    neg = ["差", "讨厌", "生气", "烂", "失望"]
    score = sum(w in text for w in pos) - sum(w in text for w in neg)
    label = "积极" if score > 0 else ("消极" if score < 0 else "中性")
    return {"label": label, "score": round(max(min(score, 3), -3) / 3, 2), "echo": text}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # 关掉默认访问日志，控制台清爽
        pass

    def _body(self) -> dict:
        """按 Content-Length 把请求体取完整。"""
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

    def _send(self, body: bytes, ctype: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code: int = 200):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8", code)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self._send(PAGE.encode("utf-8"), "text/html; charset=utf-8")
        elif url.path == "/api/health":
            self._json({"status": "ok"})
        elif url.path == "/api/sentiment":
            q = parse_qs(url.query).get("q", [""])
            self._json(fake_model(q[0]))
        else:
            self._json({"error": "接口不存在，试试 /api/sentiment?q=..."}, 404)

    def do_POST(self):
        if urlparse(self.path).path == "/api/sentiment":
            self._json(fake_model(self._body().get("text", "")))
        else:
            self._json({"error": "接口不存在"}, 404)


def serve():
    server = HTTPServer(("127.0.0.1", PORT), Handler)
    print(f"API 服务已启动：http://127.0.0.1:{PORT}（按 Ctrl+C 停止）")
    return server


def _call(method: str, path: str, payload: dict | None = None) -> str:
    """自测用小客户端：发请求，把响应完整拿回。"""
    conn = HTTPConnection("127.0.0.1", PORT, timeout=5)
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {"Content-Type": "application/json"} if body else {}
    conn.request(method, path, body=body, headers=headers)
    resp = conn.getresponse()
    buf = io.BytesIO()
    shutil.copyfileobj(resp, buf)
    conn.close()
    return buf.getvalue().decode("utf-8")


def selftest():
    server = serve()
    threading.Thread(target=server.serve_forever, daemon=True).start()
    try:
        assert "情绪分析" in _call("GET", "/"), "首页 HTML 应可访问"
        assert json.loads(_call("GET", "/api/health"))["status"] == "ok", "健康检查应 ok"
        res = json.loads(_call("GET", "/api/sentiment?q=%E5%A4%AA%E5%A5%BD%E7%94%A8%E4%BA%86"))
        assert res["label"] == "积极", f"GET 正面文本应判积极，实际 {res}"
        res2 = json.loads(_call("POST", "/api/sentiment", {"text": "太差劲了，生气"}))
        assert res2["label"] == "消极", f"POST 负面文本应判消极，实际 {res2}"
        print("selftest 通过：首页 HTML、health、GET 与 POST 接口全部正常")
    finally:
        server.shutdown()
        server.server_close()
    print("服务已关闭")


# ---------- 对照：同样的接口用 FastAPI 写（pip install fastapi uvicorn） ----------
try:
    from fastapi import FastAPI
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    print("（提示）未安装 FastAPI，真实框架段已跳过。想体验请先执行：pip install fastapi uvicorn")

if HAS_FASTAPI:
    app = FastAPI(title="AI 情绪分析 API")

    class SentimentIn(BaseModel):
        text: str

    @app.get("/api/health")
    def health():
        return {"status": "ok"}

    @app.post("/api/sentiment")
    def sentiment(item: SentimentIn):
        return fake_model(item.text)

    # 启动后访问 /docs 还有自动生成的交互式接口文档——这就是 FastAPI 的招牌

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        serve().serve_forever()
