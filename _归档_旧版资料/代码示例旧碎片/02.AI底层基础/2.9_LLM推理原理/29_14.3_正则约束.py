"""
正则表达式约束解码
"""

import outlines
from outlines.models import transformer

model = transformer("meta-llama/Llama-2-7b-chat-hf")

# 约束1: 电话号码格式
phone_pattern = r"\+86-1[3-9]\d{9}"
phone_generator = outlines.generate.regex(model, phone_pattern)

result = phone_generator("请提供一个中国手机号：")
# 输出: +86-13812345678

# 约束2: 邮箱格式
email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
email_generator = outlines.generate.regex(model, email_pattern)

result = email_generator("请提供邮箱地址：")
# 输出: user@example.com

# 约束3: 日期格式
date_pattern = r"\d{4}-\d{2}-\d{2}"
date_generator = outlines.generate.regex(model, date_pattern)

result = date_generator("今天的日期是：")
# 输出: 2024-01-15

# 约束4: 复杂格式（IP地址）
ip_pattern = r"(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)"
ip_generator = outlines.generate.regex(model, ip_pattern)

result = ip_generator("本机IP地址是：")
# 输出: 192.168.1.1
