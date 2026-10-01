"""todo.py —— 结业项目：命令行待办管理器

用法：在终端里运行 python todo.py，然后输入命令：
    add 买牛奶     添加一条待办
    list           列出全部待办
    done 1         把 1 号待办标记为完成
    delete 2       删掉 2 号待办
    exit           退出（数据自动保存到 todos.json）
"""
import json
from pathlib import Path

# 数据文件放在脚本旁边，跟代码住在一起，好找
TODOS_FILE = Path(__file__).with_name("todos.json")


def load_todos():
    # 第一次运行时 todos.json 还不存在，这不是错误，兜底返回空列表
    try:
        with open(TODOS_FILE, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_todos(todos):
    # ensure_ascii=False 让中文原样存进文件，不然会变成 \u4e70 一堆转义
    with open(TODOS_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)


def show_todos(todos):
    if not todos:
        print("（还没有待办，先用 add 加一条吧）")
        return
    print(f"你的待办（共 {len(todos)} 项）：")
    # 编号从 1 开始，跟人平时数数的习惯一致；存进列表后下标是 编号-1
    for i, item in enumerate(todos, start=1):
        mark = "已完成" if item["done"] else "未完成"
        print(f"  {i}. [{mark}] {item['text']}")


def parse_index(raw, todos):
    """把用户输入的编号转成列表下标；非法输入返回 None 并提示。

    编号可能是 abc 这种非数字，也可能超出范围，两种都要友好接住。
    """
    try:
        index = int(raw) - 1
    except ValueError:
        print("编号得是数字，比如 done 1。")
        return None
    if index < 0 or index >= len(todos):
        print(f"没有 {raw} 号待办，先 list 看看都有几号。")
        return None
    return index


def main():
    todos = load_todos()
    print("=== 待办管理器 ===")
    print("命令：add 内容 / list / done 编号 / delete 编号 / exit")
    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            # 管道喂完命令或按 Ctrl+C 退出，都算正常收场
            print()
            break
        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()

        if cmd == "exit" or cmd == "quit":
            break
        elif cmd == "add":
            if len(parts) < 2:
                print("add 后面要跟内容，比如：add 买牛奶")
                continue
            text = parts[1]
            # 任务用字典存：内容 + 完成状态；一堆字典装进列表
            todos.append({"text": text, "done": False})
            print(f"已添加：{text}")
        elif cmd == "list":
            show_todos(todos)
        elif cmd == "done":
            if len(parts) < 2:
                print("done 后面要跟编号，比如：done 1")
                continue
            index = parse_index(parts[1], todos)
            if index is not None:
                todos[index]["done"] = True
                print(f"干得漂亮：{todos[index]['text']}")
        elif cmd == "delete":
            if len(parts) < 2:
                print("delete 后面要跟编号，比如：delete 2")
                continue
            index = parse_index(parts[1], todos)
            if index is not None:
                removed = todos.pop(index)
                print(f"已删除：{removed['text']}")
        else:
            print(f"不认识「{cmd}」，可用命令：add / list / done / delete / exit")

    save_todos(todos)
    print(f"已保存到 {TODOS_FILE.name}，再见！")


if __name__ == "__main__":
    main()
