# 方法1：使用pip安装（推荐）
pip install faiss-cpu  # CPU版本

# 如果需要GPU支持
pip install faiss-gpu  # GPU版本

# 方法2：使用conda安装
conda install faiss-cpu -c conda-forge

# 方法3：从源码编译（需要完整功能）
git clone https://github.com/facebookresearch/faiss.git
cd faiss
./configure --prefix=/usr/local
make -j4
make install
