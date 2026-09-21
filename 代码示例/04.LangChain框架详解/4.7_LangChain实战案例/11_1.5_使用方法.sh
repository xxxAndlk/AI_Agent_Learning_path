# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py

# 或者使用 Docker
docker-compose up -d

# API 调用示例
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "什么是 RAG 技术？"}'
