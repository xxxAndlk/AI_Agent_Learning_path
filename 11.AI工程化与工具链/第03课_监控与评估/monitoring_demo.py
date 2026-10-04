"""monitoring_demo.py —— 最小线上监控：一批调用记录 → 聚合指标 → 阈值告警。纯标准库离线真跑。

运行：python monitoring_demo.py
（对应第 11 章第 03 课；聚合输出即第 12 章第 04 课监控 Dashboard 的雏形）
"""
import random
import statistics

THRESHOLDS = {"success_rate": 0.95, "p95_ms": 2000, "avg_tokens": 600}


def make_records(n: int = 200) -> list[dict]:
    """模拟一批调用记录。前 150 条正常，后 50 条模拟"效果衰退/异常流量"：延迟升高、错误变多。"""
    rng = random.Random(7)
    records = []
    for i in range(n):
        degraded = i >= 150
        latency = rng.gauss(800, 150) if not degraded else rng.gauss(2400, 600)
        success = rng.random() < (0.99 if not degraded else 0.86)
        records.append({
            "minute": i // 10,  # 假装每 10 条是一分钟
            "latency_ms": max(100, int(latency)),
            "success": success,
            "tokens": int(rng.gauss(420, 90)) if success else 0,
        })
    return records


def percentile(sorted_vals: list[float], p: float) -> float:
    """P95 这类分位数：排队后取第 p 名。平均数会被极端值骗，分位数更诚实。"""
    idx = min(int(len(sorted_vals) * p), len(sorted_vals) - 1)
    return sorted_vals[idx]


def aggregate(records: list[dict]) -> dict:
    lat = sorted(r["latency_ms"] for r in records)
    ok = sum(1 for r in records if r["success"])
    tokens = [r["tokens"] for r in records if r["success"]]
    return {
        "n": len(records),
        "success_rate": ok / len(records),
        "p50_ms": percentile(lat, 0.50),
        "p95_ms": percentile(lat, 0.95),
        "avg_tokens": statistics.mean(tokens) if tokens else 0.0,
    }


def check_alerts(metrics: dict) -> list[str]:
    """拿指标和阈值比，超线就生成一行带上下文的告警。"""
    alerts = []
    if metrics["success_rate"] < THRESHOLDS["success_rate"]:
        alerts.append(f"[红灯] 成功率 {metrics['success_rate']:.1%} < 阈值 {THRESHOLDS['success_rate']:.0%}（n={metrics['n']}）")
    if metrics["p95_ms"] > THRESHOLDS["p95_ms"]:
        alerts.append(f"[红灯] P95 延迟 {metrics['p95_ms']}ms > 阈值 {THRESHOLDS['p95_ms']}ms")
    if metrics["avg_tokens"] > THRESHOLDS["avg_tokens"]:
        alerts.append(f"[红灯] 平均 token {metrics['avg_tokens']:.0f} > 阈值 {THRESHOLDS['avg_tokens']}")
    return alerts


def show(title: str, m: dict) -> None:
    print(f"-- {title}（{m['n']} 条）--")
    print(f"   成功率 {m['success_rate']:.1%} | P50 {m['p50_ms']}ms | P95 {m['p95_ms']}ms | 平均 token {m['avg_tokens']:.0f}")
    alerts = check_alerts(m)
    for a in alerts:
        print("   " + a)
    if not alerts:
        print("   [绿灯] 各项指标正常")


def main() -> None:
    records = make_records()
    print("== 模拟一批线上调用（前 150 条正常，后 50 条开始衰退）==\n")

    early = [r for r in records if r["minute"] < 15]
    late = [r for r in records if r["minute"] >= 15]
    show("时段 A（正常）", aggregate(early))
    print()
    show("时段 B（衰退）", aggregate(late))

    print("\n关键观察：")
    print("1) 平均值会骗人，P95 抓住最差体验；")
    print("2) 告警必须带上下文（指标值+阈值+范围），不是一句'出事了'；")
    print("3) 聚合+阈值判断这两步，就是监控系统的心脏——Dashboard 只是把它画出来。")


if __name__ == "__main__":
    main()
