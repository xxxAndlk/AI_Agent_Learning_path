from langchain.memory import ConversationEntityMemory
from langchain_openai import ChatOpenAI
import json

llm = ChatOpenAI(model="gpt-5.4-mini")
memory = ConversationEntityMemory(llm=llm, memory_key="history")

# 实体管理的常用操作
def manage_entities():
    # 添加实体
    memory.entity_store.put("用户", {"名字": "张三", "职业": "工程师"})
    memory.entity_store.put("项目", {"名称": "AI助手", "状态": "开发中"})
    
    # 查询实体
    user = memory.entity_store.get("用户")
    print("用户信息:", user)
    
    # 获取所有实体
    all_entities = memory.entity_store.get_all()
    print("所有实体:", json.dumps(all_entities, ensure_ascii=False, indent=2))
    
    # 删除实体
    memory.entity_store.delete("项目")
    
    # 清空所有
    # memory.entity_store.clear()

manage_entities()
