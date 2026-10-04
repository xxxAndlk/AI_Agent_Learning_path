"""
自定义OutputFixingParser
展示如何自定义修复逻辑
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import (
    JsonOutputParser,
    OutputFixingParser
)
from langchain_core.runnables import RunnableLambda

# ============================================================
# 创建基础解析器
# ============================================================
json_parser = JsonOutputParser()

# ============================================================
# 自定义修复逻辑
# ============================================================
def custom_fix_logic(errors: str, completion: str, llm: str) -> str:
    """
    自定义修复逻辑
    这个函数会被OutputFixingParser内部调用
    """
    fix_prompt = f"""你是一个JSON修复专家。原始输出存在以下问题：

错误信息：
{errors}

原始输出：
{completion}

请修复JSON格式，确保：
1. 是有效的JSON
2. 保持原有数据的语义
3. 不要添加或删除必要的字段

只返回修复后的JSON，不要有其他内容。
"""
    
    # 使用LLM修复
    response = llm.invoke(fix_prompt)
    return response.content

# ============================================================
# 使用自定义修复
# ============================================================
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)

# 方式1：使用默认的OutputFixingParser
default_fixer = OutputFixingParser.from_llm(llm, json_parser)

# 方式2：通过自定义prompt（推荐）
fix_prompt_template = ChatPromptTemplate.from_template("""请修复以下JSON输出中的错误。

原始输出：
{completion}

解析错误：
{error}

要求：
1. 修复JSON语法错误
2. 保持原始数据的语义
3. 只返回修复后的JSON，不要添加解释

修复后的JSON：""")

custom_fixer = OutputFixingParser(
    parser=json_parser,
    llm=llm,
    prompt=fix_prompt_template,
    max_retries=2
)

# 测试
bad_json = '{"name": "测试", "value": incomplete'
try:
    result = custom_fixer.parse(bad_json)
    print(f"修复成功: {result}")
except Exception as e:
    print(f"错误: {e}")
