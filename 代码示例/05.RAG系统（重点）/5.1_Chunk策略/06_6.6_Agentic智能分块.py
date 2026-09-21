# Agentic分块是一种利用大语言模型智能决定分割点的方法
# 通过让LLM分析文本结构来确定最合理的分割位置

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import json

# 示例技术文档
technical_doc = """
Python是一种高级编程语言，由Guido van Rossum于1991年首次发布。
Python的设计哲学强调代码的可读性和简洁的语法。
相比于C++或Java，Python让开发者能用更少的代码完成同样的思路。

Python的核心特点包括：
1. 简洁易学的语法
2. 动态类型系统
3. 自动内存管理
4. 丰富的标准库
5. 跨平台支持

Python的应用领域非常广泛。在Web开发方面，Django和Flask是最流行的框架。
在数据科学领域，NumPy、Pandas和Matplotlib是必备工具。
在机器学习领域，TensorFlow和PyTorch是主流框架。

Python的语法非常优雅。例如，列表推导式可以用一行代码完成复杂的数据处理：
squares = [x**2 for x in range(10)]

函数的定义也很简单：
def greet(name):
    return f"Hello, {name}!"

Python的面向对象编程支持类、继承、多态等特性。
异常处理机制让程序更加健壮：
try:
    result = 10 / 0
except ZeroDivisionError:
    print("Cannot divide by zero!")

Python还支持协程和异步编程，这对于处理I/O密集型任务非常有帮助。
asyncio模块提供了对异步编程的原生支持。
"""

# 方式1：使用LLM进行智能分段
# 通过Prompt让LLM分析文档结构并返回分割点

def agentic_chunk_by_llm(text, chunk_size=500):
    """
    使用LLM进行智能分块
    LLM会分析文本的语义边界，返回最优的分割位置
    """
    # 这里需要设置OpenAI API Key
    # os.environ["OPENAI_API_KEY"] = "your-api-key"
    
    # 定义分析Prompt
    analysis_prompt = PromptTemplate.from_template("""
请分析以下技术文档的结构，找出语义边界最适合分割的位置。

要求：
1. 每个chunk应该包含完整的语义单元
2. 考虑代码示例的完整性
3. 保持主题的连贯性
4. 每个chunk目标长度为{chunk_size}字符

请返回JSON格式的分割点列表，例如：[100, 500, 900]

文档内容：
{text}
    """)
    
    # 创建LLM实例（需要API Key）
    # llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
    
    # 这里使用简单的规则作为演示
    # 实际使用时应调用LLM进行智能分析
    chunks = []
    lines = text.split('\n')
    current_chunk = ""
    
    for line in lines:
        # 检测是否是新的主题开始（通过关键字判断）
        is_new_topic = any(keyword in line for keyword in [
            "Python的", "在", "函数的", "类的", "1.", "2.", "3."
        ])
        
        if len(current_chunk) + len(line) > chunk_size and current_chunk:
            # 当前块已满，检查是否应该在这里分割
            if is_new_topic or len(current_chunk) > chunk_size * 0.8:
                # 在主题边界处分割
                chunks.append(current_chunk.strip())
                current_chunk = line + "\n"
            else:
                # 继续添加到当前块
                current_chunk += line + "\n"
        else:
            current_chunk += line + "\n"
    
    # 添加最后一个块
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks

# 执行智能分块
agentic_chunks = agentic_chunk_by_llm(technical_doc, chunk_size=400)

print(f"Agentic智能分块结果：共 {len(agentic_chunks)} 个块\n")

for i, chunk in enumerate(agentic_chunks):
    print(f"[块{i+1}] {len(chunk)}字符:")
    print(chunk[:100] + "..." if len(chunk) > 100 else chunk)
    print()
