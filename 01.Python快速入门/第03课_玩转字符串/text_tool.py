# text_tool.py —— 文本处理小工具：清空格、数字数、换词，最后出报告
# 运行：在终端里输入 python text_tool.py，按提示一句一句输入

sentence = input("请输入一段句子：")
old_word = input("想把哪个词换掉？")
new_word = input("换成什么？")

clean = sentence.strip()              # 剪掉首尾空格；中间的空格是有用的，不动
count = len(clean)                    # 数整理后的句子有多少字符
result = clean.replace(old_word, new_word)   # 旧词不在句子里时，replace 什么都不换，也不报错

print()
print("========== 处理报告 ==========")
print(f"原句　　：{sentence}")
print(f"整理后　：{result}")
print(f"字符数　：{count}（含空格）")
print(f"替换　　：{old_word} -> {new_word}")
print("==================================")
