import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.title("数据可视化演示")

# 生成示例数据
np.random.seed(42)
df = pd.DataFrame({
    "日期": pd.date_range("2024-01-01", periods=100),
    "销售额": np.random.randint(1000, 5000, 100),
    "利润": np.random.randint(100, 1000, 100),
    "类别": np.random.choice(["电子产品", "服装", "食品", "图书"], 100),
    "城市": np.random.choice(["北京", "上海", "广州", "深圳"], 100)
})

# 1. 折线图
st.header("1. 折线图")
fig_line = px.line(df, x="日期", y="销售额", title="每日销售额趋势")
st.plotly_chart(fig_line, use_container_width=True)

# 2. 柱状图
st.header("2. 柱状图")
fig_bar = px.bar(
    df.groupby("类别")["销售额"].sum().reset_index(),
    x="类别",
    y="销售额",
    title="各类别销售总额",
    color="类别"
)
st.plotly_chart(fig_bar, use_container_width=True)

# 3. 散点图
st.header("3. 散点图")
fig_scatter = px.scatter(
    df,
    x="销售额",
    y="利润",
    color="类别",
    size="销售额",
    title="销售额与利润关系",
    hover_data=["城市"]
)
st.plotly_chart(fig_scatter, use_container_width=True)

# 4. 饼图
st.header("4. 饼图")
fig_pie = px.pie(
    df,
    names="城市",
    values="销售额",
    title="各城市销售占比"
)
st.plotly_chart(fig_pie, use_container_width=True)

# 5. 热力图（使用pandas）
st.header("5. 相关性热力图")
numeric_cols = df.select_dtypes(include=[np.number]).columns
corr = df[numeric_cols].corr()
st.write(corr)

# 6. Matplotlib图表
st.header("6. Matplotlib图表")
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(df["销售额"], bins=20, edgecolor="black")
ax.set_xlabel("销售额")
ax.set_ylabel("频次")
ax.set_title("销售额分布直方图")
st.pyplot(fig)

# 7. Altair图表
st.header("7. Altair图表")
import altair as alt

chart = alt.Chart(df).mark_bar().encode(
    x="城市",
    y="sum(销售额)",
    color="城市"
).properties(title="各城市总销售额")
st.altair_chart(chart, use_container_width=True)
