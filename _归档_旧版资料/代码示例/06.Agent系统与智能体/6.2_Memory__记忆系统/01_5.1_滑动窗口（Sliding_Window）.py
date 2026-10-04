# 按消息数量滑动
while len(messages) > MAX_MESSAGES:
    messages.pop(0)  # 移除最旧的消息

# 按token数量滑动
while calculate_tokens(messages) > MAX_TOKENS:
    messages.pop(0)
