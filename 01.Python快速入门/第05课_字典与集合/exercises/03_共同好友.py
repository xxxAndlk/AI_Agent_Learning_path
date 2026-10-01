# 练习3参考答案：共同好友
# & 交集 = 两边都算好友的人；| 并集 = 合并后的全部人

my_friends = {"小明", "小红", "小刚", "阿强"}
her_friends = {"小红", "小刚", "小美", "阿花"}

print("共同好友：", my_friends & her_friends)
print("全部好友：", my_friends | her_friends)
# 集合没有固定顺序，两次运行打印的先后可能不一样，正常
