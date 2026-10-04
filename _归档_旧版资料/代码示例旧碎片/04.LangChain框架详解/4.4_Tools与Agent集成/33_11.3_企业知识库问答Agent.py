from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing import List, Dict, Optional

# ==================== 知识库模拟 ====================

class KnowledgeBase:
    """模拟企业知识库"""
    
    def __init__(self):
        self.documents = {
            "hr001": {
                "title": "员工入职指南",
                "content": """
新员工入职流程：
1. 第一天到HR部门报到，提交身份证、学历证明等材料
2. 签订劳动合同
3. 办理工卡和门禁权限
4. 领取办公用品
5. 参加入职培训（通常在入职第一周）
6. 分配导师进行一对一指导
                """,
                "category": "人力资源"
            },
            "it001": {
                "title": "IT设备申请流程",
                "content": """
IT设备申请指南：
1. 在IT服务系统提交申请
2. 部门经理审批
3. IT部门评估库存
4. 批准后领取设备
5. 签署设备领用单

常用设备：笔记本电脑、显示器、键盘鼠标
                """,
                "category": "IT支持"
            },
            "policy001": {
                "title": "考勤管理制度",
                "content": """
公司考勤制度：
- 工作时间：周一至周五 9:00-18:00
- 弹性工作制：核心时间10:00-15:00
- 加班需要部门负责人审批
- 迟到早退处理：每月3次内不计，3次外扣除绩效
                """,
                "category": "管理制度"
            }
        }
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """搜索知识库"""
        results = []
        for doc_id, doc in self.documents.items():
            if category and doc["category"] != category:
                continue
            if any(keyword in query for keyword in doc["content"]):
                results.append({
                    "id": doc_id,
                    "title": doc["title"],
                    "category": doc["category"],
                    "content": doc["content"].strip()
                })
        return results

# 初始化知识库
kb = KnowledgeBase()

# ==================== 工具定义 ====================

@tool
def search_knowledge_base(query: str, category: str = None) -> str:
    """搜索企业知识库。适用于：查找公司制度、流程指南、常见问题解答
    
    Args:
        query: 搜索关键词
        category: 可选，按类别筛选（人力资源/IT支持/管理制度）
    """
    results = kb.search(query, category)
    
    if not results:
        return "未找到相关内容，建议您换个关键词或联系IT支持"
    
    output = []
    for r in results:
        output.append(f"""
---
标题: {r['title']}
类别: {r['category']}
内容: {r['content']}
""")
    
    return "\n".join(output)

@tool
def submit_ticket(
    title: str,
    category: str,
    description: str,
    priority: str = "normal"
) -> str:
    """提交IT支持工单。用于提交问题工单到IT部门
    
    Args:
        title: 工单标题
        category: 问题类别
        description: 详细描述
        priority: 优先级 low/normal/high
    """
    import random
    ticket_id = f"TKT-{random.randint(10000, 99999)}"
    
    return f"""
工单提交成功！
工单号: {ticket_id}
标题: {title}
类别: {category}
优先级: {priority}
描述: {description}

IT部门将在24小时内处理。
"""

@tool
def get_contact_info(department: str) -> str:
    """查询部门联系方式
    
    Args:
        department: 部门名称
    """
    contacts = {
        "IT支持": "电话: 800-888-8888, 邮箱: it@company.com",
        "人力资源": "电话: 800-888-8889, 邮箱: hr@company.com",
        "行政部": "电话: 800-888-8890, 邮箱: admin@company.com",
        "财务部": "电话: 800-888-8891, 邮箱: finance@company.com"
    }
    
    dept = contacts.get(department)
    if dept:
        return f"{department}: {dept}"
    return f"未找到{department}的联系方式，可用部门: {', '.join(contacts.keys())}"

# ==================== Agent配置 ====================

tools = [
    search_knowledge_base,
    submit_ticket,
    get_contact_info
]

llm = ChatOpenAI(model="gpt-5.4", temperature=0.2)

# 使用 create_agent 创建Agent（v1.x 推荐）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""你是一个企业知识助手，专门帮助员工解决工作中的问题。

你的能力：
1. 搜索知识库 - 回答关于公司制度、流程、指南的问题
2. 提交工单 - 帮用户提交IT支持或问题反馈
3. 查询联系方式 - 提供各部门联系方式

回答要求：
- 优先从知识库中查找答案
- 如果知识库没有答案，给出建议
- 涉及到提交工单时，先确认用户的需求
- 保持专业和友好的语气
"""
)

# ==================== 使用示例 ====================

def enterprise_chat(query: str):
    """企业知识库问答接口"""
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    return result["messages"][-1].content

if __name__ == "__main__":
    # 测试问题
    print("=" * 60)
    print("用户: 如何申请新电脑？")
    print(enterprise_chat("如何申请新电脑？"))
    
    print("\n" + "=" * 60)
    print("用户: 公司的考勤时间是什么？")
    print(enterprise_chat("公司的考勤时间是什么？"))
    
    print("\n" + "=" * 60)
    print("用户: IT支持的电话是多少？")
    print(enterprise_chat("IT支持的电话是多少？"))
