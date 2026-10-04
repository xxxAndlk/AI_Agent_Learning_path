import streamlit as st

st.title("输入组件演示")

# 1. 文本输入
st.header("1. 文本输入")
text_input = st.text_input(
    "请输入您的名字：",
    placeholder="例如：张三",
    help="这是文本输入框的帮助信息"
)
st.write(f"您输入的名字是：{text_input}")

# 2. 文本区域（多行文本）
st.header("2. 文本区域")
textarea_input = st.text_area(
    "请输入您的建议：",
    height=150,
    placeholder="请详细描述您的建议..."
)
st.write(f"您输入的内容长度：{len(textarea_input)} 字符")

# 3. 数字输入
st.header("3. 数字输入")
number_input = st.number_input(
    "请选择一个数字：",
    min_value=0,
    max_value=100,
    value=50,
    step=1,
    help="选择0-100之间的数字"
)
st.write(f"选择的数字是：{number_input}")

# 4. 滑块
st.header("4. 滑块")
slider_value = st.slider(
    "调整参数",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.01,
    format="%.2f"
)
st.write(f"参数值：{slider_value}")

# 5. 选择框（下拉菜单）
st.header("5. 选择框")
selected_option = st.selectbox(
    "请选择语言：",
    ["Python", "Java", "JavaScript", "Go", "Rust"],
    index=0,
    help="选择您熟悉的编程语言"
)
st.write(f"选择的语言：{selected_option}")

# 6. 多选框
st.header("6. 多选框")
selected_options = st.multiselect(
    "请选择感兴趣的技术：",
    ["AI", "Web开发", "移动开发", "数据分析", "云计算"],
    default=["AI"]
)
st.write(f"选择的技术：{selected_options}")

# 7. 单选按钮
st.header("7. 单选按钮")
radio_option = st.radio(
    "请选择您的经验水平：",
    ["初学者", "中级", "高级", "专家"],
    horizontal=True
)
st.write(f"经验水平：{radio_option}")

# 8. 日期/时间输入
st.header("8. 日期输入")
selected_date = st.date_input(
    "选择日期："
)
st.write(f"选择的日期：{selected_date}")

# 9. 文件上传
st.header("9. 文件上传")
uploaded_file = st.file_uploader(
    "请上传文件：",
    type=["txt", "pdf", "jpg", "png"],
    help="支持 txt, pdf, jpg, png 格式"
)
if uploaded_file is not None:
    st.write(f"文件名：{uploaded_file.name}")
    st.write(f"文件大小：{uploaded_file.size} 字节")

# 10. 颜色选择器
st.header("10. 颜色选择器")
selected_color = st.color_picker(
    "选择颜色：",
    "#00FF00"
)
st.write(f"选择的颜色：{selected_color}")
