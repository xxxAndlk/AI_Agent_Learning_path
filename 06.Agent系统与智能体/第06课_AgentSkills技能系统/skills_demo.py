# 用途：纯标准库离线模拟 Agent 技能系统——技能注册、按需加载、调用与组合，全部真跑
# 运行：python skills_demo.py（零依赖、零密钥）

from datetime import datetime


class SkillRegistry:
    """技能注册表：只存'菜单'，首次调用才真正装载（按需加载）"""

    def __init__(self):
        self._menu = {}    # 名字 -> {"description", "factory": 技能类}
        self._loaded = {}  # 名字 -> 已装载的技能实例

    def register(self, description):
        """装饰器：把技能类登记进菜单（此时不创建实例）"""
        def deco(cls):
            self._menu[cls.__name__] = {"description": description, "factory": cls}
            return cls
        return deco

    def available(self):
        """列出菜单：只有名字和说明，一个技能都没装载"""
        return {name: info["description"] for name, info in self._menu.items()}

    def loaded_names(self):
        return list(self._loaded)

    def use(self, name, **kwargs):
        """按需加载并执行技能；查无此技能、执行出错都给中文兜底，不抛裸异常"""
        if name not in self._menu:
            return f"[技能缺失] 没有'{name}'这个技能。菜单上有：{'、'.join(self._menu) or '（空）'}"
        if name not in self._loaded:
            print(f"  [按需加载] 首次调用，装载技能：{name}")
            self._loaded[name] = self._menu[name]["factory"]()
        try:
            return self._loaded[name].run(**kwargs)
        except Exception as e:
            return f"[技能出错] {name} 执行失败：{e}（已兜住，Agent 可据此换路子）"


REGISTRY = SkillRegistry()

WEATHER = {"北京": "晴，12~22℃", "上海": "多云，15~21℃"}


@REGISTRY.register(description="报当前时间")
class Clock:
    def run(self):
        return f"现在是 {datetime.now():%Y-%m-%d %H:%M}"


@REGISTRY.register(description="查城市天气（离线演示表：北京/上海）")
class Weather:
    def run(self, city):
        if city not in WEATHER:
            raise ValueError(f"演示表只有北京/上海，没有'{city}'")
        return f"{city}：{WEATHER[city]}"


@REGISTRY.register(description="两数四则运算，op 取 + - * / 之一")
class Calc:
    def run(self, a, b, op):
        if op == "+":
            return a + b
        if op == "-":
            return a - b
        if op == "*":
            return a * b
        if op == "/":
            if b == 0:
                raise ValueError("除数不能为 0")
            return a / b
        raise ValueError(f"不支持的运算符'{op}'")


@REGISTRY.register(description="早间简报：组合报时+天气，一次给全")
class MorningBrief:
    def run(self, city):
        # 技能内部再调别的技能，就是"组合"
        clock = REGISTRY.use("Clock")
        weather = REGISTRY.use("Weather", city=city)
        return f"【早间简报】{clock}；{weather}"


def offline_demo():
    print("=" * 60)
    print("技能注册 → 按需加载 → 调用 → 组合（离线真跑）")
    print("=" * 60)

    print("\n1) 列菜单（注意：此时没有任何技能被装载）：")
    for name, desc in REGISTRY.available().items():
        print(f"   - {name}：{desc}")

    print("\n2) 调用 Clock 技能（观察'按需加载'提示）：")
    print("   ", REGISTRY.use("Clock"))
    print(f"    已装载：{REGISTRY.loaded_names()}")

    print("\n3) 再调一次 Clock（不会再加载）：")
    print("   ", REGISTRY.use("Clock"))

    print("\n4) 调用 Weather 技能：")
    print("   ", REGISTRY.use("Weather", city="北京"))

    print("\n5) 组合技能 MorningBrief（内部连调 Clock + Weather）：")
    print("   ", REGISTRY.use("MorningBrief", city="上海"))

    print("\n6) 故意调用不存在的技能（看菜单式兜底）：")
    print("   ", REGISTRY.use("Sing"))

    print("\n7) 技能内部出错也兜得住（Weather 收到表里没有的城市）：")
    print("   ", REGISTRY.use("Weather", city="火星"))


if __name__ == "__main__":
    offline_demo()
