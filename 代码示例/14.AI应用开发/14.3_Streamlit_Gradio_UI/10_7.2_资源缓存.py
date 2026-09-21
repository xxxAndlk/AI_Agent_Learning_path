import streamlit as st

st.title("资源缓存演示")

# 1. 模型缓存示例
@st.cache_resource
def load_model():
    """加载AI模型（只加载一次）"""
    # 模拟模型加载
    import numpy as np
    class MockModel:
        def predict(self, x):
            return x * 2
    return MockModel()

st.header("模型缓存示例")
model = load_model()
st.write(f"模型类型：{type(model)}")

if st.button("使用模型预测"):
    result = model.predict(42)
    st.write(f"预测结果：{result}")

# 2. 数据库连接缓存
@st.cache_resource
def get_database_connection():
    """缓存数据库连接"""
    # 模拟数据库连接
    return {"connected": True, "host": "localhost"}

st.header("数据库连接缓存示例")
if "db_connection" not in st.session_state:
    st.session_state.db_connection = get_database_connection()

st.write(f"数据库连接：{st.session_state.db_connection}")
