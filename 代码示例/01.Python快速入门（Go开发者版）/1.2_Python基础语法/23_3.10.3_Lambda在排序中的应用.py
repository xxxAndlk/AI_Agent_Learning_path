# ============ 列表排序与Lambda ============

# 准备一些测试数据
students = [
    {"name": "张三", "age": 25, "score": 85},
    {"name": "李四", "age": 22, "score": 92},
    {"name": "王五", "age": 28, "score": 78},
    {"name": "赵六", "age": 24, "score": 90}
]

# 按年龄排序（升序）
# sorted()函数接受key参数，指定排序依据
students_by_age = sorted(students, key=lambda s: s["age"])
print("按年龄排序:", [s["name"] for s in students_by_age])

# 按成绩排序（降序）
# 使用reverse=True实现降序
students_by_score = sorted(students, key=lambda s: s["score"], reverse=True)
print("按成绩排序:", [s["name"] for s in students_by_score])

# 按姓名长度排序
students_by_name_len = sorted(students, key=lambda s: len(s["name"]))
print("按姓名长度排序:", [s["name"] for s in students_by_name_len])

# 复杂排序：先按成绩，成绩相同按年龄
# 使用元组作为key实现多级排序
students_complex = sorted(students, key=lambda s: (s["score"], s["age"]), reverse=True)
print("先成绩后年龄:", [(s["name"], s["score"], s["age"]) for s in students_complex])

# 列表的sort()方法（原地排序）
numbers = [3, 1, 4, 1, 5, 9, 2, 6]
numbers.sort(key=lambda x: -x)
print("降序:", numbers)
