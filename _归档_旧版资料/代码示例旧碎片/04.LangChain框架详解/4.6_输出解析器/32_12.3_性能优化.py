"""
解析器性能优化
"""

# ============================================================
# 优化1：减少解析次数
# ============================================================
# 不推荐：多次调用
# for item in items:
#     result = chain.invoke(item)  # 每次都调用LLM

# 推荐：使用batch
# results = chain.batch(items)  # 批量处理

# ============================================================
# 优化2：使用流式处理
# ============================================================
# 对于大输出，使用stream避免内存问题
# for chunk in chain.stream(input):
#     process(chunk)

# ============================================================
# 优化3：选择合适的解析器
# ============================================================
# JsonOutputParser比PydanticOutputParser更轻量
# 如果不需要验证，优先使用JsonOutputParser

# ============================================================
# 优化4：缓存格式说明
# ============================================================
from langchain_core.output_parsers import JsonOutputParser

parser = JsonOutputParser()
# 格式说明可以被缓存并复用
format_instructions = parser.get_format_instructions()
