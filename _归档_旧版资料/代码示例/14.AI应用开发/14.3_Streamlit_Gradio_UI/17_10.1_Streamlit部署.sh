# 方式1：本地运行
streamlit run app.py

# 方式2：Streamlit Cloud部署
# 1. 将代码推送到GitHub
# 2. 访问 https://share.streamlit.io
# 3. 关联GitHub仓库
# 4. 设置配置并部署

# 方式3：Docker部署
# Dockerfile示例：
"""
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
"""

# 构建并运行
# docker build -t my-app .
# docker run -p 8501:8501 my-app
