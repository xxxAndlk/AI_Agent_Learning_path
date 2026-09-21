import streamlit as st

st.title("回调函数示例")

# 初始化Session State
if "form_data" not in st.session_state:
    st.session_state.form_data = {
        "name": "",
        "email": "",
        "age": 0,
        "submitted": False
    }

# 定义回调函数
def update_name():
    st.session_state.form_data["name"] = st.session_state.name_input

def update_email():
    st.session_state.form_data["email"] = st.session_state.email_input

def update_age():
    st.session_state.form_data["age"] = st.session_state.age_input

def submit_form():
    st.session_state.form_data["submitted"] = True

def clear_form():
    st.session_state.form_data = {
        "name": "",
        "email": "",
        "age": 0,
        "submitted": False
    }

# 创建表单
with st.form("user_form"):
    st.write("用户注册表单")
    
    name_input = st.text_input(
        "姓名",
        value=st.session_state.form_data["name"],
        key="name_input",
        on_change=update_name
    )
    
    email_input = st.text_input(
        "邮箱",
        value=st.session_state.form_data["email"],
        key="email_input",
        on_change=update_email
    )
    
    age_input = st.number_input(
        "年龄",
        min_value=0,
        max_value=150,
        value=st.session_state.form_data["age"],
        key="age_input",
        on_change=update_age
    )
    
    submit = st.form_submit_button("提交", on_click=submit_form)
    clear = st.form_submit_button("清空", on_click=clear_form)

# 显示提交结果
if st.session_state.form_data["submitted"]:
    st.success("表单提交成功！")
    st.json(st.session_state.form_data)
