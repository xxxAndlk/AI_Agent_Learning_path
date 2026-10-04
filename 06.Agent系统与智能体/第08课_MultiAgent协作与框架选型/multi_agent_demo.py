# 用途：纯标准库离线模拟主管-工人式 Multi-Agent 协作——拆解派活、工人接力交接、兜底与汇总
# 运行：python multi_agent_demo.py（零依赖、零密钥）

WEATHER = {"北京": "晴，12~22℃", "上海": "多云，15~21℃"}
BACKUP = {"北京": "晴，昼夜温差大", "上海": "多云转阴"}  # 兜底数据源（换路演示用）


class Worker:
    """工人 Agent：专长 description + 一门手艺 run。主管只看描述派活"""

    def __init__(self, name, description, run):
        self.name = name
        self.description = description
        self.run = run


# ---------- 三位工人 ----------

def weather_run(city, source=None):
    table = source if source is not None else WEATHER
    if city not in table:
        raise ValueError(f"{city} 不在数据表里")
    return f"{city}：{table[city]}"


def plan_run(weather):
    if "晴" in weather:
        return "天气不错，建议上午户外、下午逛馆"
    return "可能有云，建议安排室内行程为主"


def write_run(city, weather, advice):
    return f"【{city}出行简报】{weather}。{advice}。祝玩得开心！"


WORKERS = [
    Worker("天气员", "查城市天气，输入城市名", weather_run),
    Worker("规划师", "按天气给出行建议，输入天气描述", plan_run),
    Worker("文案", "把天气与建议写成简报，输入城市/天气/建议", write_run),
]

BY_NAME = {w.name: w for w in WORKERS}


def dispatch(worker_name, description, **kwargs):
    """主管派活：按名字选工人，失败时不硬扛——重派或降级，返回结果文本"""
    print(f"[主管] 派活 -> {worker_name}（{description}）")
    worker = BY_NAME.get(worker_name)
    if worker is None:
        print(f"[主管] 没有叫'{worker_name}'的工人，现有：{'、'.join(BY_NAME)}")
        return None
    try:
        out = worker.run(**kwargs)
        print(f"[{worker.name}] 交付：{out}")
        return out
    except ValueError as e:
        print(f"[{worker.name}] 失手：{e}")
        return None


def run_project(city):
    """主管视角：拆任务 -> 串行派活（交接上一步成果）-> 汇总"""
    print("=" * 60)
    print(f"任务：给{city}做一份出行简报（主管-工人模式，离线真跑）")
    print("=" * 60)

    # 第 1 步：天气员，失手后主管换兜底数据源重派（错误恢复）
    weather = dispatch("天气员", "查天气", city=city)
    if weather is None:
        print("[主管] 换备用数据源重派……")
        weather = dispatch("天气员", "查天气（备用源）", city=city, source=BACKUP)
    if weather is None:
        print("[主管] 两路都失败，如实上报：今天出不了简报")
        return

    # 第 2 步：规划师，交接：直接拿到天气员的成品
    advice = dispatch("规划师", "给建议", weather=weather)
    if advice is None:
        advice = "天气信息有限，建议室内外结合"
        print(f"[主管] 规划师缺席，主管兜底：{advice}")

    # 第 3 步：文案，交接：天气 + 建议一起递过去
    report = dispatch("文案", "写简报", city=city, weather=weather, advice=advice)

    print("\n[主管] 质检汇总，成品如下：")
    print("-" * 60)
    print(report)
    print("-" * 60)
    print("[主管] 全链路：天气员 -> 规划师 -> 文案，三次交接完成。")


if __name__ == "__main__":
    run_project("北京")   # 正常链路：三次交接一次走通
    run_project("火星")   # 失败链路：重派兜底仍失败，主管如实上报
