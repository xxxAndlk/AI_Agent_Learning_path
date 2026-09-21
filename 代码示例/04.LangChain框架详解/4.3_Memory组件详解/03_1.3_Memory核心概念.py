from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 人类消息
human_msg = HumanMessage(content="你好")

# AI消息
ai_msg = AIMessage(content="你好！有什么可以帮你的？")

# 系统消息
system_msg = SystemMessage(content="你是一个有帮助的助手")
