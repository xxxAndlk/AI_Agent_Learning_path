import streamlit as st

st.title("Session State 使用指南")

# 1. 初始化Session State
# 检查键是否存在，不存在则初始化
if "counter" not in st.session_state:
    st.session_state.counter = 0

if "user_info" not in st.session_state:
    st.session_state.user_info = {
        "name": "",
        "logged_in": False,
        "preferences": {}
    }

# 2. 使用Session State中的数据
st.write(f"当前计数：{st.session_state.counter}")

# 3. 修改Session State
col1, col2 = st.columns(2)

with col1:
    if st.button("增加计数"):
        st.session_state.counter += 1
        st.rerun()

with col2:
    if st.button("重置计数"):
        st.session_state.counter = 0
        st.rerun()

# 4. 用户信息管理示例
st.divider()
st.subheader("用户信息管理")

name = st.text_input("请输入您的名字", key="name_input")

if st.button("保存用户信息"):
    st.session_state.user_info["name"] = name
    st.session_state.user_info["logged_in"] = True
    st.success(f"欢迎，{name}！")

if st.session_state.user_info["logged_in"]:
    st.write(f"当前用户：{st.session_state.user_info['name']}")
    if st.button("退出登录"):
        st.session_state.user_info["logged_in"] = False
        st.session_state.user_info["name"] = ""
        st.rerun()
