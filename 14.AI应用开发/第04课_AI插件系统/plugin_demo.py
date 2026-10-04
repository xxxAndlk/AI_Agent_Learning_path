# -*- coding: utf-8 -*-
"""第04课配套：AI 插件系统——插件注册、发现、调用，纯标准库真跑。

本章收束课：把"可插拔"的思想变成能跑的代码，学完回第12章给项目穿上界面。

运行方式：
    python plugin_demo.py             # 跑完整演示：注册-发现-调用-开关
    python plugin_demo.py --selftest  # 自动验证后退出
"""
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")


class PluginManager:
    """插件管理中心：登记 → 列举 → 调用 → 开关。"""

    def __init__(self):
        self._plugins = {}  # name -> {"fn": ..., "description": ..., "enabled": bool}

    def register(self, name: str, description: str = ""):
        """装饰器写法：把一个函数登记成插件。"""
        def deco(fn):
            if name in self._plugins:
                raise ValueError(f"插件 {name} 已注册，不允许重复登记")
            self._plugins[name] = {"fn": fn, "description": description, "enabled": True}
            return fn
        return deco

    def discover(self, modules):
        """入口约定：每个插件模块都暴露一个 register(manager)。
        管理器不关心插件写在哪个文件、谁写的，只认这个入口——这就是"可插拔"。"""
        for mod in modules:
            mod.register(self)
        print(f"[发现] 从 {len(modules)} 个插件模块完成登记")

    def names(self):
        return list(self._plugins)

    def catalog(self):
        """给上层（比如 Agent）看的"工具清单"，相当于插件自我介绍。"""
        return [{"name": n, "description": p["description"], "enabled": p["enabled"]}
                for n, p in self._plugins.items()]

    def disable(self, name: str):
        if name in self._plugins:
            self._plugins[name]["enabled"] = False

    def enable(self, name: str):
        if name in self._plugins:
            self._plugins[name]["enabled"] = True

    def call(self, name: str, arg: str = "") -> str:
        """统一调用入口：查表 → 检查 → 执行，出错给中文提示不裸抛。"""
        plugin = self._plugins.get(name)
        if plugin is None:
            return f"[提示] 没有叫 {name} 的插件。可用：{', '.join(self.names())}"
        if not plugin["enabled"]:
            return f"[提示] 插件 {name} 已被禁用，请先 enable。"
        try:
            return plugin["fn"](arg)
        except Exception as e:  # 插件出错不能拖垮主程序
            return f"[提示] 插件 {name} 执行失败：{e}"


# ---------- 两个"插件模块"：真实项目里各是一个独立 .py 文件 ----------
class TimePlugin:
    """时间插件模块：入口约定 register(manager)。"""

    @staticmethod
    def register(manager: PluginManager):
        @manager.register("get_time", description="看看现在几点（模拟）")
        def get_time(_: str) -> str:
            return f"现在是 {time.strftime('%H:%M:%S')}（模拟时间插件）"


class TextPlugin:
    """文本插件模块：一次登记两个插件。"""

    @staticmethod
    def register(manager: PluginManager):
        @manager.register("word_count", description="统计这段话有多少字")
        def word_count(text: str) -> str:
            return f"共 {len(text)} 个字符"

        @manager.register("sentiment", description="给一句话判断情绪（关键词版）")
        def sentiment(text: str) -> str:
            pos = sum(w in text for w in ["好", "喜欢", "开心", "棒"])
            neg = sum(w in text for w in ["差", "讨厌", "生气", "烂"])
            return "积极" if pos > neg else ("消极" if neg > pos else "中性")


def main():
    manager = PluginManager()

    # 1. 发现：主程序只认入口约定，插件随到随收
    manager.discover([TimePlugin, TextPlugin])

    # 2. 列举：插件自我介绍，上层因此知道"我能干什么"
    print("\n[插件清单]")
    for item in manager.catalog():
        print(f"  - {item['name']}：{item['description']}（{'启用' if item['enabled'] else '禁用'}）")

    # 3. 调用：统一入口，像点菜一样按名调用
    print("\n[调用演示]")
    for name, arg in [("get_time", ""), ("word_count", "插件让功能即插即用"),
                      ("sentiment", "这家店服务真棒"), ("translate", "hello")]:
        print(f"  call({name!r}) -> {manager.call(name, arg)}")

    # 4. 开关：禁用后走不到函数体，主程序毫无感知
    manager.disable("sentiment")
    print(f"\n[禁用后] call('sentiment') -> {manager.call('sentiment', '真开心')}")
    manager.enable("sentiment")
    print(f"[重新启用] call('sentiment') -> {manager.call('sentiment', '真开心')}")


def selftest():
    manager = PluginManager()
    manager.discover([TimePlugin, TextPlugin])
    assert set(manager.names()) == {"get_time", "word_count", "sentiment"}, "应有 3 个插件"
    assert manager.call("word_count", "abcd") == "共 4 个字符"
    assert manager.call("sentiment", "真棒真开心") == "积极"
    assert "没有叫" in manager.call("nope"), "未知插件应给中文提示"
    manager.disable("sentiment")
    assert "禁用" in manager.call("sentiment", "x"), "禁用后应提示而非执行"
    assert "已注册" in _dup_register(manager), "重复注册应报错"
    print("selftest 通过：注册-发现-调用-开关-容错全部正常")


def _dup_register(manager: PluginManager) -> str:
    try:
        manager.register("get_time", description="重复")(lambda _: "")
        return ""
    except ValueError as e:
        return str(e)


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        main()
