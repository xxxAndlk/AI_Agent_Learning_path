import streamlit as st
import openai
from datetime import datetime

# 页面配置
st.set_page_config(
    page_title="AI助手",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = ""

if "settings" not in st.session_state:
    st.session_state.settings = {
        "model": "gpt-5.4-mini",
        "temperature": 0.7,
        "max_tokens": 2000,
        "system_prompt": "你是一个有帮助的AI助手。"
    }

# 侧边栏设置
with st.sidebar:
    st.title("⚙️ 设置")
    
    # API Key输入
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        value=st.session_state.api_key,
        help="请输入您的OpenAI API Key"
    )
    st.session_state.api_key = api_key
    
    st.divider()
    
    # 模型选择
    model = st.selectbox(
        "选择模型",
        ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-pro"],
        index=["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-pro"].index(
            st.session_state.settings["model"]
        )
    )
    st.session_state.settings["model"] = model
    
    # 参数调节
    st.subheader("模型参数")
    temperature = st.slider(
        "Temperature", 0.0, 2.0, 
        st.session_state.settings["temperature"],
        help="值越高，输出越随机"
    )
    max_tokens = st.slider(
        "Max Tokens", 100, 4000, 
        st.session_state.settings["max_tokens"],
        help="最大生成token数"
    )
    st.session_state.settings["temperature"] = temperature
    st.session_state.settings["max_tokens"] = max_tokens
    
    st.divider()
    
    # 系统提示词
    system_prompt = st.text_area(
        "系统提示词",
        value=st.session_state.settings["system_prompt"],
        height=100
    )
    st.session_state.settings["system_prompt"] = system_prompt
    
    st.divider()
    
    # 操作按钮
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💾 保存设置", use_container_width=True):
            st.success("设置已保存")
    with col2:
        if st.button("🗑️ 清空对话", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
    
    # 会话统计
    st.divider()
    st.metric("对话轮数", len(st.session_state.messages))

# 主界面
st.title("🤖 AI助手")
st.markdown("基于OpenAI的聊天机器人")

# 显示聊天历史
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        
        # 显示时间戳
        if "timestamp" in message:
            st.caption(f"🕐 {message['timestamp']}")
        
        # 显示token使用（如果是assistant消息）
        if message["role"] == "assistant" and "usage" in message:
            st.caption(f"📊 使用Token: {message['usage']}")

# 用户输入
if prompt := st.chat_input("输入消息..."):
    # 验证API Key
    if not api_key:
        st.error("请在侧边栏输入API Key")
        st.stop()
    
    # 添加用户消息
    user_message = {
        "role": "user",
        "content": prompt,
        "timestamp": datetime.now().strftime("%H:%M:%S")
    }
    st.session_state.messages.append(user_message)
    
    # 显示用户消息
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # 构建消息列表
    messages = [
        {"role": "system", "content": system_prompt}
    ]
    messages.extend([
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ])
    
    # 生成AI回复
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""
        
        try:
            client = openai.OpenAI(api_key=api_key)
            
            # 流式生成
            stream = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
            # 保存助手回复
            assistant_message = {
                "role": "assistant",
                "content": full_response,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.messages.append(assistant_message)
            
        except Exception as e:
            st.error(f"调用API出错：{str(e)}")
