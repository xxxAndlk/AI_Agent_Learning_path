# Agent 任务执行系统（第 02 课实战项目）

## 这是干什么的

给 Agent 一个总任务，它自己拆解成子任务、挑选工具、一步步执行，每一步打印"思考-行动-观察"，最后汇报总结。用来理解 Agent 循环与工具注册的最小完整实现。

## 怎么装

零依赖：装好 Python 3.9+ 即可，不需要 pip install 任何东西。

## 怎么跑

```
python agent_runner.py                     # 内置演示：查标准 -> 算账 -> 记备忘
python agent_runner.py "查一下VPN申请流程"   # 自定任务，看它换执行路径
```

## 文件说明

| 文件 | 说明 |
|------|------|
| 第02课.md | 讲义：Agent 循环、架构图、代码导读 |
| agent_runner.py | 核心程序，约 160 行，纯标准库 |

## 接下来可以改

- 换大脑：把 `plan()`/`choose_tool()` 换成 LLM 输出计划 JSON（需 API Key）
- 换工具：`TOOLBOX` 里接入真实 API；第 12.5 课会做成 MCP 平台统一管理
- 学完第 14 章回来：用 FastAPI + WebSocket 做一个实时展示执行过程的前端页面
