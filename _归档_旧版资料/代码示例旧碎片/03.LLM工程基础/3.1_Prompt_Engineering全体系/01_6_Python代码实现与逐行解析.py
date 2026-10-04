from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# 配置项：模型名 / API密钥 / 访问地址
MODEL = os.getenv("MODEL", "deepseek-v4-flash")        # 模型名称
API_KEY = os.getenv("API_KEY")  # API密钥
BASE_URL = os.getenv("URL")  # API 地址

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,  # 传 None 则走官方默认地址
)

def few_shot_example():
    """Few-Shot Learning（少样本学习）示例

    通过在提示中提供几个示例，让模型学习任务的模式
    """
    # 构建Few-Shot提示
    # 提供3个示例（文本->情感），然后让模型预测最后一个
    prompt = """
    分类以下文本的情感：
    文本: "这电影太好看了！"
    情感: 积极
    文本: "今天天气真糟糕。"
    情感: 消极
    文本: "这顿饭还行。"
    情感: 中性
    文本: "我对这次服务非常满意！"
    情感:
    """
    
    # 调用模型
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # 提取并打印模型的回答
    content = response.choices[0].message.content
    print("Few-Shot结果:", content.strip() if content else "（模型未返回文本内容）")

def cot_example():
    """Chain-of-Thought（思维链）示例
    
    通过展示推理过程，让模型学会逐步思考复杂问题
    """
    # CoT提示：提供详细的解题步骤
    prompt = """
    问题: 一个农场有鸡和兔子，共30个头，84只脚。问鸡和兔子各有多少只？
    思考过程: 让我们一步步来思考。
    1. 设鸡的数量为x，兔子的数量为y。
    2. 根据头的数量：x + y = 30
    3. 根据脚的数量：2x + 4y = 84
    4. 从第一个方程得：x = 30 - y
    5. 代入第二个方程：2(30 - y) + 4y = 84 → 60 - 2y + 4y = 84 → 2y = 24 → y = 12
    6. 则x = 30 - 12 = 18
    答案: 鸡18只，兔子12只。
    
    问题: 小明买了3个苹果和2个橘子，共花了18元；买2个苹果和3个橘子，共花了17元。问苹果和橘子的单价各是多少？
    思考过程:
    """
    
    # 调用API（复用之前的client）
    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}]
    )

    content = response.choices[0].message.content
    print("CoT结果:\n", content if content else "（模型未返回文本内容）")

if __name__ == "__main__":
    # 可以单独运行某个示例
    few_shot_example()
    cot_example()
    # print("请取消注释运行需要的示例")
