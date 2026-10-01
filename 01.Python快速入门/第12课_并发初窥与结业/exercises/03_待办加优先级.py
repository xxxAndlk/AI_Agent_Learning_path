"""练习3参考答案：待办加优先级
给任务字典加一个 priority 字段（数字越小越要紧），
按优先级排序后再显示——这就是把 todo.py 往"更顺手"改的思路。
"""
todos = [
    {"text": "回老板消息", "priority": 1},
    {"text": "写周报", "priority": 2},
    {"text": "刷一会儿视频", "priority": 3},
]

# sort 的 key 参数：告诉它"按什么排"。这里用一行小函数取出每条任务的 priority
# （第 11 课见过的 lambda：lambda t: t["priority"] 等价于一个返回 t["priority"] 的小函数）
todos.sort(key=lambda t: t["priority"])

print("按优先级排序后：")
for i, item in enumerate(todos, start=1):
    print(f"  {i}. [P{item['priority']}] {item['text']}")

# 想接进 todo.py 的话：add 时多问一句优先级存进字典，
# list 时先 sort 再打印，剩下的逻辑一概不用动。
