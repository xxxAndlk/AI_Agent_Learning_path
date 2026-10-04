# 获取当前摘要
current_summary = memory.load_memory_variables({})
print("当前摘要:", current_summary["history"])

# 直接访问moving_summary属性
print("\n原始摘要文本:")
print(memory.moving_summary)

# 查看是否还在使用原始消息
print(f"\n缓冲消息数: {len(memory.chat_memory.messages)}")
