# 练习 3：九九乘法表（必做）
# 要点：两层 for 嵌套。外层管"第几行"，内层管"这一行里打几个算式"。
# 对齐诀窍：f-string 里写 {row * col:>2}，让结果右对齐占 2 格，1 位和 2 位数不错位。

for row in range(1, 10):           # 第 1 行到第 9 行
    for col in range(1, row + 1):  # 第 row 行只有 row 个算式，所以内层到 row + 1（不含）
        print(f"{col}×{row}={row * col:>2}", end="  ")  # end="  "：打完不换行，隔两个空格接着打
    print()                        # 一行打完，换行
