# uvicorn配置与部署

# 方式1：直接运行
# uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 方式2：程序内配置
if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        workers=4,  # 工作进程数，建议设置为CPU核心数的2倍+1
        reload=False,  # 生产环境关闭
        log_level="info",
        access_log=True,
        timeout_keep_alive=30,
        limit_concurrency=1000,
        limit_max_requests=10000,  # 每个worker处理这么多请求后重启
    )


# Gunicorn + Uvicorn Workers (推荐生产部署)
# gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用nginx反向代理配置示例
"""
nginx配置:

upstream fastapi {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
    server 127.0.0.1:8003;
}

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://fastapi;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /path/to/static/files;
    }
}
"""

# Docker部署
"""
Dockerfile:

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
"""

# docker-compose.yml
"""
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/aiapp
    depends_on:
      - db
    restart: always

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=aiapp
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""

# 性能优化建议
"""
1. 减少同步阻塞操作：
   - 使用异步数据库驱动（asyncpg, aiosqlite）
   - 将CPU密集型任务放到线程池

2. 添加缓存：
   - 使用Redis缓存频繁访问的数据
   - 添加HTTP缓存头

3. 启用压缩：
   - app.add_middleware(GZipMiddleware, minimum_size=1000)

4. 限流保护：
   - 使用slowapi进行请求限流
   
5. 监控和日志：
   - 集成Prometheus指标
   - 结构化日志记录
"""

# 限流示例
# pip install slowapi
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

@api_router.post("/ai/chat")
@limiter.limit("10/minute")  # 每分钟10次请求
async def chat(request: Request):
    # ...
"""
