# 创建同步任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "计算 100 * 25 + 50 的结果"}'

# 创建异步任务
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "搜索Python教程", "async_mode": true}'

# 查询任务状态
curl http://localhost:8000/api/tasks/task_abc123

# 获取统计信息
curl http://localhost:8000/api/statistics

# WebSocket连接
# 使用WebSocket客户端连接到 ws://localhost:8000/ws
