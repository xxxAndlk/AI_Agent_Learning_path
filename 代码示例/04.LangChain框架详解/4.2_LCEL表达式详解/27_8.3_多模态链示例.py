"""
多模态链实现示例
展示如何处理文本和图像的组合输入
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from PIL import Image
import io
import base64

# 模拟多模态LLM（实际需要使用支持视觉的模型）
llm = ChatOpenAI(model="gpt-5.4-vision-preview")

# ============================================================
# 辅助函数：图像处理
# ============================================================

def encode_image_to_base64(image_path: str) -> str:
    """将图像编码为base64字符串"""
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def create_image_message(image_base64: str) -> dict:
    """创建图像消息格式"""
    return {
        "type": "image_url",
        "image_url": {
            "url": f"data:image/jpeg;base64,{image_base64}"
        }
    }

# ============================================================
# 多模态问答链
# ============================================================

def build_multimodal_chain():
    """构建多模态问答链"""
    
    def prepare_multimodal_input(inputs: dict):
        """准备多模态输入"""
        text = inputs.get("text", "")
        image_path = inputs.get("image", None)
        
        if image_path:
            # 如果有图像，添加图像到消息
            image_base64 = encode_image_to_base64(image_path)
            image_message = create_image_message(image_base64)
            
            return [
                {"type": "text", "text": text},
                image_message
            ]
        else:
            return text
    
    # 创建多模态提示模板
    multimodal_prompt = ChatPromptTemplate.from_messages([
        ("user", [
            {"type": "text", "text": "{text}"},
            {"type": "image_url", "image_url": {"url": "{image}"}}
        ])
    ])
    
    # 注意：实际使用时需要使用支持视觉的模型
    # 这里使用模拟的方式展示结构
    chain = (
        RunnableLambda(prepare_multimodal_input)
        | multimodal_prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

# 创建链
# multimodal_chain = build_multimodal_chain()

# 使用示例（需要实际的图像文件）
# result = multimodal_chain.invoke({
#     "text": "描述这张图片中的内容",
#     "image": "./image.jpg"
# })

print("多模态链的完整实现需要使用GPT-5.4V等支持视觉的模型")
print("上述代码展示了基本的结构和思路")
