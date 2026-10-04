import streamlit as st
import pandas as pd
import numpy as np

st.title("数据显示组件演示")

# 1. 指标卡片
st.header("1. 指标卡片")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="总用户数", value="1,234", delta="+12%")
with col2:
    st.metric(label="活跃用户", value="890", delta="-5%", delta_color="inverse")
with col3:
    st.metric(label="总收入", value="$56,789", delta="$1,234")
with col4:
    st.metric(label="转化率", value="3.21%", delta="0.12%")

# 2. 表格显示
st.header("2. 表格显示")
data = {
    "姓名": ["张三", "李四", "王五", "赵六"],
    "年龄": [25, 30, 35, 28],
    "城市": ["北京", "上海", "广州", "深圳"],
    "职业": ["工程师", "设计师", "产品经理", "数据分析师"]
}
df = pd.DataFrame(data)
st.table(df)

# 3. DataFrame交互展示
st.header("3. DataFrame交互展示")
st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "姓名": st.column_config.TextColumn("姓名", width="medium"),
        "年龄": st.column_config.NumberColumn("年龄", format="%d 岁"),
        "城市": st.column_config.TextColumn("城市"),
        "职业": st.column_config.TextColumn("职业")
    }
)

# 4. JSON显示
st.header("4. JSON显示")
json_data = {
    "name": "Streamlit",
    "version": "1.30.0",
    "features": ["快速开发", "实时交互", "数据可视化"],
    "config": {
        "theme": "dark",
        "language": "zh"
    }
}
st.json(json_data)

# 5. 代码显示
st.header("5. 代码显示")
code = """
def hello_world():
    print("Hello, Streamlit!")
    return "Hello, World!"

result = hello_world()
"""
st.code(code, language="python")

# 6. 进度条
st.header("6. 进度条")
progress = st.progress(0)
for i in range(100):
    progress.progress(i + 1)

# 7. 加载动画
st.header("7. 加载动画")
with st.spinner("正在处理中..."):
    import time
    time.sleep(2)
st.success("处理完成！")

# 8. 消息提示
st.header("8. 消息提示")
st.info("这是一条信息")
st.success("操作成功！")
st.warning("警告信息")
st.error("错误信息")

# 9. 展开/折叠
st.header("9. 展开/折叠")
with st.expander("点击展开更多内容"):
    st.write("这是隐藏的详细内容...")
    st.write("可以包含更多的组件和数据")

# 10. 容器容器
st.header("10. 容器")
with st.container(border=True):
    st.write("这是一个带边框的容器")
    st.button("容器内的按钮")
