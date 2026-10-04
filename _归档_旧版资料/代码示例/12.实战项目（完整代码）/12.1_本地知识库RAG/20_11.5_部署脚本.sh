#!/bin/bash
# deploy.sh
# Docker部署脚本

set -e

echo "🚀 开始部署RAG应用..."

# 1. 检查环境变量
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️ 警告: 未设置OPENAI_API_KEY环境变量"
    echo "请设置: export OPENAI_API_KEY=your-api-key"
fi

# 2. 构建Docker镜像
echo "📦 构建Docker镜像..."
docker-compose -f docker/docker-compose.yml build

# 3. 启动服务
echo "▶️ 启动服务..."
docker-compose -f docker/docker-compose.yml up -d

# 4. 等待服务就绪
echo "⏳ 等待服务就绪..."
sleep 10

# 5. 检查服务状态
echo "🔍 检查服务状态..."
docker-compose -f docker/docker-compose.yml ps

echo "✅ 部署完成！"
echo "访问地址: http://localhost:8501"

# 6. 查看日志
echo ""
echo "📝 查看日志: docker-compose -f docker/docker-compose.yml logs -f"
