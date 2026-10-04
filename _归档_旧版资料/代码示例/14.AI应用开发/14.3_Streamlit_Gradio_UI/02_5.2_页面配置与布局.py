import streamlit as st

# 页面配置（必须在最开头设置）
st.set_page_config(
    page_title="AI应用演示",          # 页面标题
    page_icon="🤖",                   # 页面图标（emoji或URL）
    layout="wide",                   # 布局：'wide'或'centered'
    initial_sidebar_state="expanded",  # 侧边栏状态
    menu_items={
        "Get Help": "https://example.com/help",
        "Report a Bug": "https://example.com/bug",
        "About": "## 关于本应用\n这是一个AI应用演示。"
    }
)

# 使用st.title设置主标题
st.title("🤖 智能问答助手")

# 使用st.markdown添加说明
st.markdown("""
这是一个基于大语言模型的智能问答助手。
您可以在左侧配置参数，并向助手提问。
""")

# 使用st.divider添加分隔线
st.divider()

# 多列布局
col1, col2, col3 = st.columns([2, 1, 1])

with col1:
    st.header("主内容区")
    st.write("这是主要内容区域")

with col2:
    st.header("侧边栏")
    st.write("辅助信息")

with col3:
    st.header("工具区")
    st.write("快捷操作")
