import itertools

# 场景：日志分析
logs = [
    {'time': '2024-01-01 10:00:00', 'level': 'INFO', 'msg': 'Server started'},
    {'time': '2024-01-01 10:00:02', 'level': 'ERROR', 'msg': 'Connection failed'},
    {'time': '2024-01-01 10:00:04', 'level': 'ERROR', 'msg': 'Connection failed'},
    {'time': '2024-01-01 10:00:05', 'level': 'INFO', 'msg': 'Success'},
]

# 1. 过滤错误日志
errors = itertools.filterfalse(lambda x: x['level'] != 'ERROR', logs)
# 2. 提取消息
error_msgs = map(lambda x: x['msg'], errors)
# 3. 去重并排序
unique_msgs = sorted(set(error_msgs))
print("错误消息列表:", unique_msgs)
# ['Connection failed']
