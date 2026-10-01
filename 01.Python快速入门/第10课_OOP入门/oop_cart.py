# oop_cart.py —— 第10课课上小程序：用类改写购物车
# 第4课的 shopping_cart.py 里，清单数据和加、删、打印的动作是分开的两摊。
# 这次把数据和动作装进同一个类，体会"数据和操作绑在一起"。

class ShoppingCart:
    def __init__(self):
        # 每辆新车出厂都是空的。一项商品长这样：{"名称": "牛奶", "单价": 5, "数量": 2}
        self.items = []

    def add(self, name, price, quantity):
        # 已经在车里就直接加数量，不另起一项——不然"牛奶"会出现两行
        for item in self.items:
            if item["名称"] == name:
                item["数量"] += quantity
                return
        self.items.append({"名称": name, "单价": price, "数量": quantity})

    def remove(self, name):
        for item in self.items:
            if item["名称"] == name:
                self.items.remove(item)
                return
        # 第4课说过：直接删不存在的东西会报错。先找再删，程序就不会崩
        print(f"购物车里没有{name}，删不了")

    def show(self):
        print("=== 购物车明细 ===")
        if not self.items:
            print("（空的）")
            return
        for item in self.items:
            subtotal = item["单价"] * item["数量"]
            print(f"{item['名称']}　{item['单价']}元 × {item['数量']} = {subtotal}元")

    def total(self):
        total_price = 0
        for item in self.items:
            total_price += item["单价"] * item["数量"]
        # 浮点数算钱会长出 0.30000000000000004 这样的尾巴，用 round 收干净
        return round(total_price, 2)


# ---- 演示：造一辆车，加3样、删1样 ----

cart = ShoppingCart()
cart.add("牛奶", 5, 2)
cart.add("面包", 8, 1)
cart.add("苹果", 3, 4)

# 控糖，面包不买了
cart.remove("面包")
# 牛奶消耗快，再囤一盒——同名商品会直接加数量
cart.add("牛奶", 5, 1)

cart.show()
print("一共", cart.total(), "元")

# 再造一辆车，验证两辆车互不干扰
another = ShoppingCart()
another.add("酱油", 12, 1)
print("另一辆车：", another.total(), "元——它可不知道牛奶是什么")
