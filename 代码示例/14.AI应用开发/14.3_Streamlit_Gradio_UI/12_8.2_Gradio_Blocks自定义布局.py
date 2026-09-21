import gradio as gr

with gr.Blocks(title="自定义AI聊天应用") as demo:
    gr.Markdown("# 🤖 AI聊天助手")
    
    with gr.Row():
        with gr.Column(scale=3):
            chatbot = gr.Chatbot(
                label="对话历史",
                height=400,
                bubble_full_width=False
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
            
            model_select = gr.Dropdown(
                ["GPT-5.4", "GPT-5.4-nano", "Claude"],
                value="GPT-5.4-nano",
                label="选择模型"
            )
            
            temperature = gr.Slider(
                0, 2, 0.7,
                step=0.1,
                label="Temperature",
                info="控制生成随机性"
            )
            
            max_tokens = gr.Slider(
                100, 4000, 1000,
                step=100,
                label="Max Tokens",
                info="最大生成长度"
            )
    
    def respond(message, history, model, temp, tokens):
        # 模拟AI响应
        response = f"模型: {model}\nTemp: {temp}\nTokens: {tokens}\n\n"
        if "你好" in message:
            response += "你好！有什么可以帮助你的吗？"
        elif "天气" in message:
            response += "今天天气晴朗，适合外出。"
        else:
            response += f"你刚才说：{message}\n这是一个模拟的AI响应。"
        
        history.append((message, response))
        return "", history
    
    submit_btn.click(
        respond,
        inputs=[msg, chatbot, model_select, temperature, max_tokens],
        outputs=[msg, chatbot]
    )
    
    msg.submit(
        respond,
        inputs=[msg, chatbot, model_select, temperature, max_tokens],
        outputs=[msg, chatbot]
    )
    
    clear_btn.click(lambda: (None, []) , outputs=[msg, chatbot])

# demo.launch()
