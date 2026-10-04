# MCP 智能工具集成平台（第 05 课实战项目）

## 这是干什么的

纯标准库模拟的 MCP 工具平台：多个工具（数据库/GitHub/Slack）统一注册到 Server，Client 走标准流程"握手 → 发现工具 → 调用 → 结果回填"。消息形状对齐真实 MCP 协议（initialize / tools/list / tools/call），用于理解"工具即插即用"的协议设计。

## 怎么装

零依赖：装好 Python 3.9+ 即可，不需要 pip install 任何东西。

## 怎么跑

```
python mcp_platform.py
```

演示含四阶段全流程 + 一次故意失败调用（看标准错误结构）+ 调用历史。

## 文件说明

| 文件 | 说明 |
|------|------|
| 第05课.md | 讲义：MCP 解决什么、四阶段流程、代码导读 |
| mcp_platform.py | 核心程序，约 170 行，纯标准库 |

## 接下来可以改

- 注册你自己的工具：`server.register(名字, 说明, 参数表, 函数)`
- 学完第 14 章回来：用 FastAPI 把 `MCPServer.handle()` 包成 HTTP 接口，升级为跨进程真协议
- 进阶：装官方 MCP SDK 跑真 Server（第 6 章第 05 课有最小实操）
