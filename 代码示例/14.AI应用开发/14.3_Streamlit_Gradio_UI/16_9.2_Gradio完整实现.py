import gradio as gr
import openai
from datetime import datetime

# 历史记录
history = []

def chat(message, history, model, temperature, max_tokens, api_key):
    """聊天函数"""
    if not api_key:
        return "请输入API Key", history
    
    # 构建消息列表
    messages = [{"role": "system", "content": "你是一个有帮助的AI助手。"}]
    
    for user_msg, bot_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": bot_msg})
    
    messages.append({"role": "user", "content": message})
    
    # 调用API
    try:
        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        bot_message = response.choices[0].message.content
        history.append((message, bot_message))
        
        return "", history
    
    except Exception as e:
        return f"错误：{str(e)}", history

# 创建界面
with gr.Blocks(title="AI聊天助手", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 AI聊天助手")
    gr.Markdown("基于OpenAI的智能对话应用")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="对话历史",
                height=500,
                avatar_images=(None, "🤖")
            )
            
            with gr.Row():
                msg = gr.Textbox(
                    label="输入消息",
                    placeholder="请输入您的问题...",
                    lines=3,
                    show_label=False
                )
            
            with gr.Row():
                submit_btn = gr.Button("发送", variant="primary")
                clear_btn = gr.Button("清空对话")
        
        with gr.Column(scale=1):
            gr.Markdown("### ⚙️ 设置")
            
            api_key = gr.Textbox(
                label="API Key",
                type="password",
                placeholder="sk-..."
            )
            
            model = gr.Dropdown(
                ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-pro"],
                value="gpt-5.4-mini",
                label="模型"
            )
            
            temperature = gr.Slider(
                0, 2, 0.7,
                step=0.1,
                label="Temperature"
            )
            
            max_tokens = gr.Slider(
                100, 4000, 2000,
                step=100,
                label="Max Tokens"
            )
    
    # 事件处理
    submit_btn.click(
        chat,
        inputs=[msg, chatbot, model, temperature, max_tokens, api_key],
        outputs=[msg, chatbot]
    )
    
    msg.submit(
        chat,
        inputs=[msg, chatbot, model, temperature, max_tokens, api_key],
        outputs=[msg, chatbot]
    )
    
    clear_btn.click(
        lambda: (None, []),
        outputs=[msg, chatbot]
    )
    
    # 示例
    gr.Examples(
        examples=[
            ["你好，请介绍一下自己"],
            ["什么是机器学习？"],
            ["给我讲一个笑话"]
        ],
        inputs=msg
    )

# demo.launch()
