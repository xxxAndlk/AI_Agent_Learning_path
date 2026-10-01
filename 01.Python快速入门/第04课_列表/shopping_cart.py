# shopping_cart.py —— 第04课课上小程序：购物清单
# 只用到列表和 for。为什么没有"你输入要加什么"的交互菜单？
# 因为那需要第 6 课的循环和判断——完整的菜单系统是第 12 课结业项目。

shopping = ["牛奶", "面包", "鸡蛋", "苹果"]

print("=== 出门前的购物清单 ===")
for item in shopping:
    print("- " + item)

# 到楼下想起酱油也见底了，添到清单末尾
shopping.append("酱油")

# 开始控糖，面包不买了
# remove 按"值"删，只删第一个匹配的；删列表里没有的值会报错
shopping.remove("面包")

print()
print("=== 更新后的购物清单 ===")
for item in shopping:
    print("- " + item)

print()
print("一共要买", len(shopping), "样东西")
