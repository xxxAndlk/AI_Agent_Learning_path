# 练习 2 参考答案：并排配对
# zip 把两个等长列表合成一对一对，enumerate 再给结果编号

goods = ["牛奶", "面包", "鸡蛋", "苹果"]
prices = [6.5, 8, 12, 5.8]

pairs = list(zip(goods, prices))  # [(名称, 价格), ...] 一对一对的元组
print("配对结果:", pairs)

print("--- 购物小票 ---")
for i, (name, price) in enumerate(pairs, start=1):
    # start=1 让序号从 1 开始，更符合小票习惯
    print(f"{i}. {name}　{price} 元")
