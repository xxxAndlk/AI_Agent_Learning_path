# 安装faiss-gpu（选择与CUDA版本匹配的版本）
pip install faiss-gpu==1.7.2  # CUDA 11.x
# 或者
pip install faiss-gpu-cu11    # conda安装CUDA 11版本

# 验证安装
python -c "import faiss; print(faiss.GpuResources)"
