# 监控消息数量和估算Token
def estimate_tokens(memory):
    """估算内存中的Token数量"""
    total_chars = sum(
        len(msg.content) for msg in memory.chat_memory.messages
    )
    # 粗略估算：1个Token约等于4个字符
    return total_chars // 4

memory = ConversationBufferMemory(memory_key="history", return_messages=True)

# 添加一些对话
for i in range(5):
    memory.chat_memory.add_user_message(f"用户问题{i}")
    memory.chat_memory.add_ai_message(f"AI回答{i}")

print(f"消息数量: {len(memory.chat_memory.messages)}")
print(f"估算Token数: {estimate_tokens(memory)}")
