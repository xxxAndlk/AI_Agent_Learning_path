# -*- coding: utf-8 -*-
"""第03课配套：几乎不写前端搭 AI 界面——Streamlit 与 Gradio 的两种脑回路。

零依赖段（默认运行）：纯标准库模拟"输入 → 调模型 → 展示"的界面数据流，真跑。
真实框架段：Streamlit / Gradio 写法对照，需先安装：pip install streamlit / pip install gradio

运行方式：
    python ui_demo.py                 # 跑零依赖模拟，看清界面背后的数据流
    streamlit run ui_demo.py          # 装了 Streamlit 的话，直接变成真界面（自动识别）
    python ui_demo.py --selftest      # 自动验证数据流后退出
"""
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def model(question: str) -> str:
    """假装是大模型：内置几条问答，其余统一客套。真实项目换成大模型调用。"""
    canned = {
        "什么是rag": "RAG 就是先查资料再回答：把知识库里的相关片段塞进提示词，让模型照着答。",
        "什么是embedding": "Embedding 把文字变成一串数字（向量），意思相近的文字，向量也相近。",
    }
    return canned.get(question.lower().replace(" ", ""),
                      f"（模拟模型）关于「{question}」我会在这里给出回答，此处省略两百字。")


def streamlit_style():
    """Streamlit 脑回路：每次交互，整个脚本从头到尾重跑一遍，状态靠 session 存。"""
    print("=== Streamlit 式：脚本重跑模式 ===")
    session = {"history": []}  # 相当于 st.session_state

    def run_script(user_input: str, clicked: bool) -> str:
        screen = []
        screen.append(f"[输入框] 当前内容：{user_input}")       # st.text_input
        if clicked:                                            # st.button 只在点击瞬间为真
            session["history"].append((user_input, model(user_input)))
        for i, (q, a) in enumerate(session["history"], 1):
            screen.append(f"Q{i}：{q}")
            screen.append(f"A{i}：{a}")
        return "\n".join(screen)

    # 模拟三轮交互：打字不触发模型，点击才触发，历史一直在
    print(run_script("什么是 RAG", False), "\n--- 打字不调模型 ↑ ---")
    print(run_script("什么是 RAG", True), "\n--- 点击提问 ↑ ---")
    print(run_script("什么是 Embedding", True), "\n--- 第二问，历史还在 ↑ ---")
    return session


def gradio_style():
    """Gradio 脑回路：声明"函数 + 输入组件 + 输出组件"，每次提交回调一次。"""
    print("=== Gradio 式：回调模式 ===")

    def ask(question: str, temperature: float = 0.7) -> str:
        return model(question)

    interface = {"fn": ask, "inputs": ["Textbox", "Slider"], "outputs": "Textbox"}
    print(f"界面声明：fn={interface['fn'].__name__}，"
          f"输入={interface['inputs']}，输出={interface['outputs']}")
    print("用户点提交 → Gradio 自动取组件值调用 fn → 结果填进输出框")
    print("输出示例：" + interface["fn"]("你好，介绍一下你自己"))
    return interface


# ---------- 对照：真 Streamlit 界面（pip install streamlit） ----------
try:
    import streamlit as st
    HAS_ST = True
except ImportError:
    HAS_ST = False
    print("（提示）未安装 Streamlit，真实界面段已跳过。想体验请先执行：pip install streamlit")


def streamlit_app():
    """真界面：streamlit run ui_demo.py 时从这里进。"""
    st.title("迷你问答机器人")
    q = st.text_input("输入你的问题")
    if st.button("提问") and q:
        with st.spinner("思考中…"):
            st.write(model(q))
    if st.session_state.get("log"):
        st.subheader("聊天记录")
        for i, (qq, aa) in enumerate(st.session_state["log"], 1):
            st.text(f"Q{i}：{qq}\nA{i}：{aa}")


def _in_streamlit_runtime() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False


if HAS_ST:
    if _in_streamlit_runtime():
        # 把每次问答记进 session_state，脚本重跑历史不丢
        if "log" not in st.session_state:
            st.session_state["log"] = []
        _q = st.text_input("输入你的问题")
        if st.button("提问") and _q:
            _a = model(_q)
            st.session_state["log"].append((_q, _a))
            st.write(_a)
        for i, (qq, aa) in enumerate(st.session_state["log"], 1):
            st.text(f"Q{i}：{qq}  A{i}：{aa}")


# ---------- 对照：真 Gradio 界面（pip install gradio） ----------
try:
    import gradio as gr
    HAS_GR = True
except ImportError:
    HAS_GR = False
    print("（提示）未安装 Gradio，真实界面段已跳过。想体验请先执行：pip install gradio")

if HAS_GR:
    def launch_gradio():
        demo = gr.Interface(
            fn=lambda q, t: model(q),
            inputs=[gr.Textbox(label="问题"), gr.Slider(0, 1, 0.7, label="温度（本演示未用）")],
            outputs=gr.Textbox(label="回答"),
            title="迷你问答机器人")
        demo.launch()
    # 学生装好 gradio 后，取消下一行注释即可真跑：
    # launch_gradio()


def selftest():
    session = streamlit_style()
    assert len(session["history"]) == 2, "点击两次应产生两条问答记录"
    assert session["history"][0][0] == "什么是 RAG", "第一问应为 RAG"
    interface = gradio_style()
    assert interface["fn"]("什么是rag").startswith("RAG"), "回调应取到模拟模型结果"
    print("selftest 通过：脚本重跑模式与回调模式的数据流均正常")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--gradio" in sys.argv and HAS_GR:
        launch_gradio()
    elif HAS_ST and _in_streamlit_runtime():
        pass  # Streamlit 运行时已执行上面的界面代码
    else:
        streamlit_style()
        print()
        gradio_style()
