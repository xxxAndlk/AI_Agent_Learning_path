from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory(
    # 核心参数
    memory_key="history",           # 内存变量在prompt中的键名
    return_messages=True,           # True返回消息对象，False返回字符串
    
    # 消息过滤（可选）
    output_key="text",              # 从输出中提取AI回复
    input_key="question",           # 从输入中提取用户问题
    
    # 高级选项
    human_prefix="用户",            # 人类消息前缀
    ai_prefix="助手",               # AI消息前缀
    
    # 聊天消息历史（可自定义存储后端）
    chat_memory=...,                # 自定义消息存储实现
)
