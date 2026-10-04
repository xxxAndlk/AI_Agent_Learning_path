# 用途：离线模拟 MCP（模型上下文协议）的最小握手与工具调用，看清 JSON-RPC 消息的真实形状
# 运行：python mcp_demo.py（第 1 段零依赖，纯标准库，离线真跑）
# 可选：第 2 段需要 mcp 库（pip install mcp），未安装会中文提示并跳过；该段未实跑

import json

PROTOCOL_VERSION = "2024-11-05"


class MiniMCPServer:
    """最小 MCP Server：登记工具，按 JSON-RPC 2.0 的形状应答"""

    def __init__(self, name="mini-mcp-server", version="0.1"):
        self.server_info = {"name": name, "version": version}
        self.tools = {}  # 工具名 -> {"description", "input_schema", "func"}

    def tool(self, description, input_schema):
        """装饰器：把普通函数登记成 MCP 工具（名字、说明、参数模式）"""
        def deco(func):
            self.tools[func.__name__] = {
                "description": description,
                "input_schema": input_schema,
                "func": func,
            }
            return func
        return deco

    def handle(self, message):
        """收一条请求(dict)，返回应答(dict)；通知(notification)返回 None"""
        method = message.get("method", "")
        if method == "initialize":
            result = {
                "protocolVersion": PROTOCOL_VERSION,
                "serverInfo": self.server_info,
                "capabilities": {"tools": {}},
            }
            return self._reply(message, result=result)
        if method == "notifications/initialized":
            return None  # 通知不带 id，也不需要应答
        if method == "tools/list":
            menu = [
                {"name": n, "description": t["description"], "inputSchema": t["input_schema"]}
                for n, t in self.tools.items()
            ]
            return self._reply(message, result={"tools": menu})
        if method == "tools/call":
            params = message.get("params", {})
            name, args = params.get("name", ""), params.get("arguments", {})
            if name not in self.tools:
                return self._reply(message, error={"code": -32602, "message": f"未知工具: {name}"})
            try:
                out = self.tools[name]["func"](**args)
            except TypeError as e:
                return self._reply(message, error={"code": -32602, "message": f"参数不对: {e}"})
            return self._reply(message, result={"content": [{"type": "text", "text": str(out)}]})
        return self._reply(message, error={"code": -32601, "message": f"未知方法: {method}"})

    @staticmethod
    def _reply(message, result=None, error=None):
        reply = {"jsonrpc": "2.0", "id": message.get("id")}
        if error is not None:
            reply["error"] = error
        else:
            reply["result"] = result
        return reply


def make_server():
    server = MiniMCPServer()

    @server.tool(
        description="查询某城市当前天气（离线演示数据）",
        input_schema={"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    )
    def get_weather(city):
        fake = {"北京": "晴，12~22℃", "上海": "多云，15~21℃"}
        return fake.get(city, f"{city}：暂无演示数据（示例表只有北京/上海）")

    @server.tool(
        description="两数相加",
        input_schema={"type": "object", "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}}},
    )
    def add(a, b):
        return a + b

    return server


def send(server, req_id, method, params=None):
    """Client 发请求并打印双方消息——重点是看清 JSON 形状"""
    request = {"jsonrpc": "2.0", "method": method}
    if req_id is not None:
        request["id"] = req_id
    if params is not None:
        request["params"] = params
    print("\n【Client → Server】")
    print(json.dumps(request, ensure_ascii=False, indent=2))
    if method == "notifications/initialized":
        print("（通知没有 id，Server 无须应答）")
        return
    print("【Server → Client】")
    print(json.dumps(server.handle(request), ensure_ascii=False, indent=2))


def offline_demo():
    """离线主戏：握手 → 看菜单 → 点单 → 出错，全部真跑"""
    print("=" * 60)
    print("第 1 段（离线真跑）：迷你 MCP 握手与工具调用")
    print("=" * 60)
    server = make_server()
    send(server, 1, "initialize", {
        "protocolVersion": PROTOCOL_VERSION,
        "capabilities": {},
        "clientInfo": {"name": "mini-client", "version": "0.1"},
    })
    send(server, None, "notifications/initialized")
    send(server, 2, "tools/list")
    send(server, 3, "tools/call", {"name": "get_weather", "arguments": {"city": "北京"}})
    send(server, 4, "tools/call", {"name": "add", "arguments": {"a": 2, "b": 40}})
    print("\n故意调用一个不存在的工具，看错误应答的形状：")
    send(server, 5, "tools/call", {"name": "no_such_tool", "arguments": {}})


def real_mcp_segment():
    """真实 MCP 段：需要 pip install mcp。只演示定义方式，不在本课实跑服务器（未实跑）"""
    print("\n" + "=" * 60)
    print("第 2 段（需 mcp 库，未实跑）：真实 FastMCP 工具定义长什么样")
    print("=" * 60)
    try:
        from mcp.server.fastmcp import FastMCP  # noqa: F401
    except ImportError:
        print("未安装 mcp 库，跳过本段；想跑可先执行 pip install mcp")
        return
    print("已检测到 mcp 库。真实服务器这样定义（完整写法见讲义）：")
    print("  mcp = FastMCP('我的工具箱')；@mcp.tool() 装饰一个函数；mcp.run() 以 stdio 模式启动")
    print("本脚本只做定义演示、不真正启动服务（run 会阻塞终端）；涉及远程调用与 Key 的部分未实跑。")


if __name__ == "__main__":
    offline_demo()
    real_mcp_segment()
