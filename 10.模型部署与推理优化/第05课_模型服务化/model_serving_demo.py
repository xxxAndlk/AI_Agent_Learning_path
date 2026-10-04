# -*- coding: utf-8 -*-
"""模型服务化演示：网关路由+限流计数器、最小HTTP API、扩缩容直觉模拟。

全程纯标准库，零依赖直接运行：python model_serving_demo.py
"""
import json
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LINE = "-" * 52


def banner(title):
    print(f"\n{LINE}\n{title}\n{LINE}")


# ---------- 第 1 段：网关路由 + 限流计数器（纯逻辑） ----------

ROUTES = {  # 请求类型 -> 模型后端（客户端只认网关一个入口）
    "chat": "chat-model-v2",
    "embed": "embedding-model",
    "summary": "chat-model-mini",
}


class RateLimiter:
    """固定窗口计数器：窗口内每键超过 limit 次即拒收。"""

    def __init__(self, limit, window_sec=60):
        self.limit = limit
        self.window = window_sec
        self.counter = {}

    def allow(self, key):
        now = time.time()
        start, used = self.counter.get(key, (now, 0))
        if now - start >= self.window:      # 窗口滑过，重置
            start, used = now, 0
        if used >= self.limit:
            self.counter[key] = (start, used)
            return False
        self.counter[key] = (start, used + 1)
        return True


def run_gateway_demo():
    banner("第 1 段：网关路由 + 限流计数器（模拟）")
    limiter = RateLimiter(limit=5)          # 每用户每窗口 5 次
    requests = [("u1", "chat")] * 3 + [("u1", "embed")] * 4 + [("u2", "chat")] * 2
    for i, (user, kind) in enumerate(requests, 1):
        backend = ROUTES[kind]
        if limiter.allow(user):
            print(f"  #{i} 用户{user} {kind:8s} -> {backend}  [200 通过]")
        else:
            print(f"  #{i} 用户{user} {kind:8s} -> 已拒收      [429 太频繁，稍后再试]")
    print("要点: 路由表让后端可随时替换；计数器超限即拒，保护的是所有正常用户。")


# ---------- 第 2 段：最小 HTTP API（标准库真起服务） ----------

LAST_REPLY = {}     # 进程内记录最近一次回复，供演示打印（避免客户端重复取正文）


class MiniHandler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(url.query)
        if url.path == "/health":
            self._send(200, {"status": "ok"})
        elif url.path == "/chat":
            msg = qs.get("msg", [""])[0][:200]
            LAST_REPLY["chat"] = {"reply": f"已收到: {msg}", "prompt_tokens": len(msg)}
            self._send(200, LAST_REPLY["chat"])
        else:
            self._send(404, {"error": "unknown path"})

    def log_message(self, *args):           # 静默默认访问日志，输出由演示统一打印
        pass


def run_http_demo():
    banner("第 2 段：最小 HTTP API（真起服务、自测、关闭）")
    server = ThreadingHTTPServer(("127.0.0.1", 0), MiniHandler)  # 端口 0=系统自动挑空闲
    port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{port}"
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=5) as resp:
            print(f"GET /health       -> HTTP {resp.status}")
        msg = urllib.parse.quote("你好服务化")   # 查询串含中文须 percent-encode
        with urllib.request.urlopen(f"{base}/chat?msg={msg}", timeout=5) as resp:
            print(f"GET /chat?msg=... -> HTTP {resp.status}")
        print(f"对话接口返回的 JSON: {LAST_REPLY.get('chat')}")
    finally:
        server.shutdown()
        server.server_close()
        print("服务已干净关闭（生产级服务=同样的骨架+鉴权/日志/HTTPS）。")


# ---------- 第 3 段：扩缩容直觉 ----------

def run_scaling_demo():
    banner("第 3 段：扩缩容 —— 人多开窗口，人少收窗口")
    load_trace = [4, 9, 14, 11, 6, 2]   # 各时段并发请求数；每副本可扛 5 并发
    REPLICA_CAP = 5
    total_cost = 0
    print("时段  负载  副本数(向上取整)  累计副本·时段(≈成本)")
    for t, load in enumerate(load_trace, 1):
        replicas = -(-load // REPLICA_CAP)
        total_cost += replicas
        print(f"  t{t}   {load:2d}        {replicas}                {total_cost}")
    fixed = 3   # 按峰值固定开 3 副本
    print(f"按峰值固定 {fixed} 副本 -> 成本 {fixed * len(load_trace)}"
          f" | 自动扩缩容 -> 成本 {total_cost}（低谷不养闲兵）")
    print("交换: 自动化省成本，但要求监控灵敏——反应慢半拍高峰就排队。")


def main():
    print("第 05 课配套演示：模型服务化（纯标准库，零依赖）")
    run_gateway_demo()
    run_http_demo()
    run_scaling_demo()
    print("\n全部演示结束。服务只是开始——下一章让服务'可管理'。")


if __name__ == "__main__":
    main()
