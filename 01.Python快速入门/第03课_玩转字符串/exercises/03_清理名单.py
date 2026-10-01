# 03_清理名单.py —— 把格式很脏的逗号名单整理整齐
# 输入示例：张三, 李四 ,  王五   （空格忽多忽少）
# 输出：张三, 李四, 王五
# 思路：split(",") 切开 -> 每个名字 strip() -> ", ".join 缝回去

raw = input("请输入用逗号隔开的名字：")
parts = raw.split(",")                # 切开后每个名字前后可能挂着空格

names = []
for name in parts:                    # for 是第 6 课的主角，这里先照着写：把 parts 里每个名字挨个处理一遍
    names.append(name.strip())        # strip 掉每个名字首尾的空格，再放回 names 这个列表

print("整理后的名单：" + ", ".join(names))
