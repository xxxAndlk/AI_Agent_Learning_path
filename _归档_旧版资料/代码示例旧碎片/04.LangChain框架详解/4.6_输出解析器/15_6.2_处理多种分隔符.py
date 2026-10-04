"""
CommaSeparatedListOutputParser处理多种分隔符
展示解析器的灵活性
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import CommaSeparatedListOutputParser
from langchain_core.documents import HumanMessage

# ============================================================
# 创建解析器
# ============================================================
parser = CommaSeparatedListOutputParser()

# ============================================================
# 测试不同格式的输入
# ============================================================
test_cases = [
    # 情况1：逗号分隔
    "苹果, 香蕉, 橙子, 葡萄",
    
    # 情况2：换行分隔
    """苹果
香蕉
橙子
葡萄""",
    
    # 情况3：混合分隔
    "苹果, 香蕉\n橙子; 葡萄",
    
    # 情况4：编号列表
    """1. 苹果
2. 香蕉
3. 橙子""",
    
    # 情况5：带连字符
    """- 苹果
- 香蕉
- 橙子"""
]

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

for i, test_input in enumerate(test_cases, 1):
    # 直接调用parse方法测试
    result = parser.parse(test_input)
    print(f"测试{i}: {result}")
