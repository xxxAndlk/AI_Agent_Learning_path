import gradio as gr

# 基础示例：文本分类器
def classify_text(text, model_type):
    """简单的文本分类函数"""
    if not text:
        return "", {}
    
    # 模拟分类
    keywords = ["好", "棒", "优秀", "喜欢"]
    if any(k in text for k in keywords):
        sentiment = "正面"
        confidence = 0.95
    else:
        sentiment = "中性"
        confidence = 0.60
    
    return sentiment, {"正面": confidence, "中性": 1-confidence, "负面": 1-confidence}

# 创建Interface
demo = gr.Interface(
    fn=classify_text,
    inputs=[
        gr.Textbox(label="输入文本", placeholder="请输入要分类的文本..."),
        gr.Dropdown(["基础模型", "高级模型"], label="选择模型")
    ],
    outputs=[
        gr.Label(label="分类结果"),
        gr.JSON(label="详细置信度")
    ],
    title="文本情感分类器",
    description="输入文本，选择模型类型，获取情感分类结果",
    theme="default",
    examples=[["这个产品很好用！"], ["一般般，没什么特别的"]]
)

# 启动应用
# demo.launch()
