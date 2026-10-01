# ledger.py —— 记账本：程序关掉，账还在。
# 运行：python ledger.py，连跑两次，看看账目怎么变多。

def add_records():
    # a 模式追加：文件不存在会自动创建，存在就在末尾接着写
    with open("records.txt", "a", encoding="utf-8") as f:
        f.write("买午饭,-25\n")      # write 不自动换行，行尾要自己补 \n
        f.write("发工资,8000\n")
        f.write("买书,-68\n")


def show_balance():
    # 第一次运行时 records.txt 可能还没建出来，所以读取要放进 try 里
    try:
        with open("records.txt", "r", encoding="utf-8") as f:
            total = 0
            rows = []
            for line in f:                   # 逐行读，比一次全读省内存
                line = line.strip()          # 脱掉行尾看不见的换行符
                if line == "":
                    continue                 # 空行不算账
                note, amount = line.split(",")   # 按逗号拆成说明和金额
                total = total + int(amount)
                rows.append(note + " " + amount + " 元")
        for row in rows:
            print(row)
        print("—— 以上是全部账目 ——")
        print("当前结余：", total, "元")
    except FileNotFoundError:
        print("账本还不存在，先记一笔吧。")


add_records()    # 第一段：先记账
show_balance()   # 第二段：再对账
