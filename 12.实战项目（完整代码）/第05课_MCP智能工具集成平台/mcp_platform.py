# -*- coding: utf-8 -*-
"""MCP 智能工具集成平台（第05课实战项目）：多工具统一注册/握手/发现/调用，纯标准库模拟协议。

零依赖可跑（纯标准库；消息形状对齐真实 MCP 的 initialize / tools/list / tools/call）：
    python mcp_platform.py
"""

import json
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ---------------------------------------------------------------- 模拟工具
# 每个工具 = 函数 + 清单条目（说明+参数描述）。Agent 靠清单选工具，说明必须写清楚。
DB = {"员工数": "128 人", "本月营收": "¥ 3,200,000", "在招岗位": "算法工程师 2 名"}


def db_query(sql_like):
    """模拟数据库查询（关键字匹配演示）。"""
    for k, v in DB.items():
        if k in sql_like:
            return f"查询结果：{k} = {v}"
    return f"查询结果：无「{sql_like}」相关记录"


def github_repo_info(repo):
    """模拟查 GitHub 仓库信息。"""
    return f"仓库 {repo}：开放 issue 23 个，最近一次提交 2 小时前，主要语言 Python"


def slack_send(channel, text):
    """模拟发 Slack 消息（只打印不真发）。"""
    return f"已向 #{channel} 发送消息：「{text}」"


# ---------------------------------------------------------------- Server
class MCPServer:
    """工具平台：注册表 + 协议入口 handle()。Client 只能通过 handle() 交互。"""

    PROTOCOL = "mcp-sim/1.0"

    def __init__(self, name="tools-platform"):
        self.name = name
        self.registry = {}   # 工具名 -> (函数, 参数表描述)
        self.catalog = {}    # 工具名 -> 给 Agent 看的说明
        self.history = []    # 调用历史：审计/排查用

    def register(self, name, desc, params, func):
        self.registry[name] = (func, params)
        self.catalog[name] = desc

    # ---- 协议入口：所有请求都是 {"method": ..., "params": ...} 字典 ----
    def handle(self, request):
        method, params = request.get("method"), request.get("params", {})
        handlers = {
            "initialize": self._on_initialize,
            "tools/list": self._on_list,
            "tools/call": self._on_call,
        }
        h = handlers.get(method)
        if h is None:
            return {"isError": True, "error": f"未知方法 {method!r}，支持：{sorted(handlers)}"}
        return h(params)

    def _on_initialize(self, params):
        return {"isError": False, "protocol": self.PROTOCOL,
                "server": self.name, "capabilities": ["tools"]}

    def _on_list(self, _):
        return {"isError": False, "tools": [
            {"name": n, "description": d, "params": self.registry[n][1]}
            for n, d in self.catalog.items()
        ]}

    def _on_call(self, params):
        name = params.get("name", "")
        if name not in self.registry:
            return {"isError": True, "error": f"工具 {name!r} 未注册，请先 tools/list 查看可用工具"}
        func, _ = self.registry[name]
        t0 = time.perf_counter()
        try:
            result = func(**params.get("arguments", {}))
        except TypeError as e:
            return {"isError": True, "error": f"参数不匹配：{e}"}
        except Exception as e:
            return {"isError": True, "error": f"工具执行失败：{e}"}
        rec = {"tool": name, "ms": round((time.perf_counter() - t0) * 1000, 1)}
        self.history.append(rec)
        return {"isError": False, "result": result}


# ---------------------------------------------------------------- Client
class MCPClient:
    """Agent 侧：只发标准请求，不 import 任何工具函数——Server 随便换实现。"""

    def __init__(self, server):
        self.server = server
        self.tools = []  # 发现回来的工具清单

    def connect(self):
        resp = self.server.handle({"method": "initialize", "params": {"client": "agent"}})
        print(f"[握手] 协议={resp['protocol']} server={resp['server']} 能力={resp['capabilities']}")
        return resp

    def discover(self):
        resp = self.server.handle({"method": "tools/list"})
        self.tools = resp["tools"]
        return self.tools

    def call(self, name, **arguments):
        return self.server.handle({"method": "tools/call",
                                   "params": {"name": name, "arguments": arguments}})


# ---------------------------------------------------------------- 演示
def demo():
    server = MCPServer()
    server.register("db_query", "查询公司内部数据，如员工数/营收/岗位", {"sql_like": "查询关键词"}, db_query)
    server.register("github_repo_info", "查 GitHub 仓库的活跃度信息", {"repo": "仓库全名"}, github_repo_info)
    server.register("slack_send", "向指定频道发送一条消息", {"channel": "频道名", "text": "消息内容"}, slack_send)

    client = MCPClient(server)
    client.connect()

    print("\n[发现] tools/list 返回的工具清单：")
    for t in client.discover():
        print(f"  · {t['name']}（参数：{t['params']}）—— {t['description']}")

    print("\n[调用] 依次执行三个工具：")
    demos = [
        ("db_query", {"sql_like": "本月营收"}),
        ("github_repo_info", {"repo": "our-ai/agent"}),
        ("slack_send", {"channel": "team-ai", "text": "本周实验报告已同步"}),
    ]
    for name, args in demos:
        resp = client.call(name, **args)
        print(f"  {name} -> {json.dumps(resp, ensure_ascii=False)}")

    print("\n[容错] 调用未注册的工具：")
    print(f"  {json.dumps(client.call('weather_query', city='上海'), ensure_ascii=False)}")

    print(f"\n[历史] 平台共记录 {len(server.history)} 次调用：{server.history}")
    print("提示：Client 全程没有 import 任何工具函数——换掉整个 Server 实现，Client 一行不用改。")


if __name__ == "__main__":
    demo()
