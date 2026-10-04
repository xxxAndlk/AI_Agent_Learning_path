import streamlit as st

st.title("组件键值管理")

# 情况1：循环中创建组件需要唯一的key
st.subheader("示例1：循环中的组件")

cols = st.columns(3)
for i, col in enumerate(cols):
    with col:
        # 每次循环使用不同的key
        value = st.text_input(
            f"输入{i+1}",
            key=f"input_{i}"
        )
        st.write(f"值：{value}")

# 情况2：条件渲染的组件
st.subheader("示例2：条件渲染的组件")

show_extra = st.checkbox("显示更多选项")

if show_extra:
    extra_value = st.text_input("额外输入", key="extra")
    st.write(f"额外输入：{extra_value}")
else:
    st.info("勾选上方复选框显示更多选项")

# 情况3：动态添加/删除组件
st.subheader("示例3：动态组件")

if "inputs" not in st.session_state:
    st.session_state.inputs = []

# 添加新输入
if st.button("添加输入框"):
    st.session_state.inputs.append(len(st.session_state.inputs))

# 显示所有输入
for idx in st.session_state.inputs:
    col1, col2 = st.columns([4, 1])
    with col1:
        val = st.text_input(f"输入 {idx+1}", key=f"dynamic_{idx}")
    with col2:
        if st.button("删除", key=f"delete_{idx}"):
            st.session_state.inputs.remove(idx)
            st.rerun()

# 显示所有值
if st.session_state.inputs:
    st.write("所有输入：")
    for idx in st.session_state.inputs:
        st.write(f"输入 {idx+1}: {st.session_state.get(f'dynamic_{idx}', '')}")
