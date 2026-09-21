# 1. 克隆项目
git clone <project-url>
cd rag_project

# 2. 配置环境变量
cp .env.example .env
# 编辑.env文件，填入API Key

# 3. 准备文档
mkdir -p data/docs
# 将文档放入data/docs目录

# 4. 使用Docker部署
chmod +x deploy.sh
./deploy.sh

# 5. 访问应用
# 浏览器打开 http://localhost:8501

# 6. 管理命令
# 查看日志
docker-compose -f docker/docker-compose.yml logs -f

# 停止服务
docker-compose -f docker/docker-compose.yml down

# 重新构建
docker-compose -f docker/docker-compose.yml build --no-cache
docker-compose -f docker/docker-compose.yml up -d
