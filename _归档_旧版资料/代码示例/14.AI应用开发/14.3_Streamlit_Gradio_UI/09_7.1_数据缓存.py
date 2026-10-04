import streamlit as st
import time

st.title("缓存机制演示")

# 1. 基础缓存示例
@st.cache_data
def load_data():
    """模拟从数据库加载数据"""
    time.sleep(2)  # 模拟耗时操作
    return {"data": [1, 2, 3, 4, 5], "timestamp": time.time()}

st.header("基础缓存示例")
if st.button("加载数据"):
    with st.spinner("加载中..."):
        result = load_data()
    st.write(f"数据：{result['data']}")
    st.write(f"加载时间：{result['timestamp']}")

# 2. 带参数的缓存函数
@st.cache_data
def fetch_user_data(user_id, page=1):
    """模拟从API获取用户数据"""
    time.sleep(1)
    return {
        "user_id": user_id,
        "page": page,
        "name": f"用户{user_id}",
        "data": list(range(page * 10))
    }

st.header("带参数缓存示例")
user_id = st.number_input("用户ID", min_value=1, max_value=100, value=1)
page = st.slider("页码", 1, 10, 1)

if st.button("获取用户数据"):
    data = fetch_user_data(user_id, page)
    st.json(data)

# 3. 缓存条件失效
@st.cache_data(ttl=60)  # 60秒后缓存失效
def get_data_with_ttl():
    """带过期时间的缓存"""
    return {"time": time.time()}

st.header("缓存过期示例")
if st.button("获取数据（60秒后过期）"):
    st.write(get_data_with_ttl())

# 4. 清除缓存
@st.cache_data
def expensive_function(x):
    return x ** 2

st.header("清除缓存示例")
if st.button("计算（使用缓存）"):
    result = expensive_function(100)
    st.write(f"结果：{result}")

if st.button("清除缓存"):
    st.cache_data.clear()
    st.success("缓存已清除")
