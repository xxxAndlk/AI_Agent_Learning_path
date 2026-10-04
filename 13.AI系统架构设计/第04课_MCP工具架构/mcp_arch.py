# mcp_arch.py —— MCP 工具架构骨架（第13章第04课配套）
# 用途：纯标准库模拟 MCP Client/Server 双方：握手 → 发现 → 调用 的协议三步曲
# 运行：python mcp_arch.py   零依赖零Key，直接真跑

import json


def msg(method, params=None, mid=None):
    """标准形状的协议消息（jsonrpc 风格，与真实 MCP 消息形似）。"""
    return {"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}}


# ============ Server：能力包装车间 ============
class McpServer:
    def __init__(self, name):
        self.name = name
        self.tools = {}   # 工具名 -> {desc, params, fn}

    def tool(self, name, desc, params):
        def deco(fn):
            self.tools[name] = {"desc": desc, "params": params, "fn": fn}
            return fn
        return deco

    def handle(self, request):
        """Server 只认协议消息，不认人——Client 和它之间没有别的通道。"""
        m, p = request["method"], request["params"]
        if m == "initialize":
            return {"server": self.name, "protocol": "2026-xx", "capabilities": ["tools", "resources"]}
        if m == "tools/list":
            return [{"name": n, "description": t["desc"], "params": t["params"]} for n, t in self.tools.items()]
        if m == "tools/call":
            t = self.tools.get(p["name"])
            if not t:
                return {"error": f"工具 {p['name']} 不存在"}
            try:
                return {"result": t["fn"](**p.get("args", {}))}
            except Exception as e:
                return {"error": f"工具执行失败：{e}"}
        return {"error": f"未知方法 {m}"}


# ============ 两个独立 Server：文档部 & 数据部 ============
DOC_SERVER = McpServer("doc-server")

@DOC_SERVER.tool("search_docs", "按关键词搜索公司文档，返回标题列表", {"query": "string"})
def search_docs(query):
    return ["报销制度v3.docx", "年假政策.docx"] if "假" in query or "报销" in query else []

@DOC_SERVER.tool("read_doc", "读取指定文档的正文（演示返回摘要）", {"title": "string"})
def read_doc(title):
    return f"《{title}》摘要：入职满一年享五天年假…"


DATA_SERVER = McpServer("data-server")

@DATA_SERVER.tool("query_sales", "查询某季度销售额（万元）", {"quarter": "string"})
def query_sales(quarter):
    return {"2026Q1": 120, "2026Q2": 135}.get(quarter, 0)


# ============ Client：传令兵 ============
class McpClient:
    def __init__(self):
        self.conns = {}  # server名 -> server对象

    def connect(self, server):
        """握手：报家门、协商版本。谈不拢就拒绝接入。"""
        reply = server.handle(msg("initialize", {"client": "mini-host", "version": "2026-xx"}, mid=1))
        assert reply["protocol"] == "2026-xx", "协议版本协商失败"
        self.conns[reply["server"]] = server
        print(f"[Client] 与 {reply['server']} 握手成功（能力：{reply['capabilities']}）")

    def discover(self):
        """发现：把所有 Server 的工具汇成一份统一清单（Host 只看这份）。"""
        catalog = []
        for name, srv in self.conns.items():
            for t in srv.handle(msg("tools/list", {}, mid=2)):
                catalog.append({"server": name, **t})
        return catalog

    def call(self, server_name, tool, args):
        out = self.conns[server_name].handle(msg("tools/call", {"name": tool, "args": args}, mid=3))
        return out.get("result", f"错误：{out.get('error')}")


if __name__ == "__main__":
    client = McpClient()
    print("=" * 60)
    print("第 1 步：握手（每个 Server 一次，版本协商）")
    print("=" * 60)
    client.connect(DOC_SERVER)
    client.connect(DATA_SERVER)
    print()
    print("=" * 60)
    print("第 2 步：发现（两Server的工具汇成统一清单，Host 只看这份）")
    print("=" * 60)
    catalog = client.discover()
    for t in catalog:
        print(f"  [{t['server']}] {t['name']}：{t['description']} 参数：{t['params']}")
    print()
    print("=" * 60)
    print("第 3 步：调用（按清单路由到对应 Server，Host 不关心实现）")
    print("=" * 60)
    print("调用 search_docs('年假') ->", client.call("doc-server", "search_docs", {"query": "年假"}))
    print("调用 read_doc(...)      ->", client.call("doc-server", "read_doc", {"title": "年假政策.docx"}))
    print("调用 query_sales(...)   ->", client.call("data-server", "query_sales", {"quarter": "2026Q1"}))
    print("调用不存在的工具        ->", client.call("data-server", "hack_db", {}))
    print()
    print(json.dumps({"注": "消息形状为jsonrpc风格dict，与真实MCP消息形似"}, ensure_ascii=False))
