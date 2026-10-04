# -*- coding: utf-8 -*-
"""模型性能监控 Dashboard（第04课实战项目）：采集延迟/token/成功率 -> 聚合报告 + 阈值告警。

零依赖可跑（纯标准库）：
    python monitor_dashboard.py                       # 内置模拟数据全流程演示
    python monitor_dashboard.py ask "翻译这段话"        # 演示单次调用的记录与统计
"""

import sys
import time
import uuid

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# 告警阈值：业务决定，改这里即可
THRESHOLDS = {"min_success_rate": 0.90, "max_p95_ms": 2000.0}

CALLS = []  # 采集层：真实系统中对应日志/时间序列库的一行


# ---------------------------------------------------------------- 采集
def record_call(name, latency_ms, tokens, ok, error=""):
    """每次模型调用记一条。trace_id 是这次调用的身份证，可顺着翻原始日志。"""
    CALLS.append({
        "trace_id": uuid.uuid4().hex[:8],
        "ts": time.strftime("%H:%M:%S"),
        "name": name,
        "latency_ms": latency_ms,
        "tokens": tokens,
        "ok": ok,
        "error": error,
    })
    return CALLS[-1]["trace_id"]


# ---------------------------------------------------------------- 聚合
def p95(values):
    """P95：排序后取 95% 位置的值，代表"最倒霉的 5% 用户"的体验。"""
    vs = sorted(values)
    idx = min(int(len(vs) * 0.95), len(vs) - 1)
    return vs[idx]


def aggregate(calls=None):
    """按调用名分组，算次数/成功率/平均延迟/P95/平均token。"""
    calls = CALLS if calls is None else calls
    groups = {}
    for c in calls:
        groups.setdefault(c["name"], []).append(c)
    stats = {}
    for name, items in groups.items():
        n = len(items)
        ok_n = sum(1 for c in items if c["ok"])
        stats[name] = {
            "n": n,
            "success_rate": ok_n / n,
            "avg_ms": sum(c["latency_ms"] for c in items) / n,
            "p95_ms": p95([c["latency_ms"] for c in items]),
            "avg_tokens": sum(c["tokens"] for c in items) / n,
        }
    return stats


# ---------------------------------------------------------------- 告警
def check_alerts(stats):
    alerts = []
    for name, s in stats.items():
        if s["success_rate"] < THRESHOLDS["min_success_rate"]:
            alerts.append(f"[成功率] {name} 成功率 {s['success_rate']:.0%}，低于 {THRESHOLDS['min_success_rate']:.0%}")
        if s["p95_ms"] > THRESHOLDS["max_p95_ms"]:
            alerts.append(f"[延迟] {name} P95 {s['p95_ms']:.0f}ms，超过 {THRESHOLDS['max_p95_ms']:.0f}ms")
    return alerts


# ---------------------------------------------------------------- 报告
def render_report(stats, alerts):
    print("=" * 66)
    print("模型性能监控报告（CLI 版 · 承接第 11 章监控/可观测性）")
    print("=" * 66)
    head = f"{'调用':<14}{'次数':>4}{'成功率':>8}{'平均ms':>9}{'P95ms':>9}{'均值tok':>9}"
    print(head)
    print("-" * 66)
    for name, s in stats.items():
        print(f"{name:<14}{s['n']:>4}{s['success_rate']:>7.0%}{s['avg_ms']:>9.0f}"
              f"{s['p95_ms']:>9.0f}{s['avg_tokens']:>9.1f}")
    print("-" * 66)
    if alerts:
        print(f"⚠ 告警 {len(alerts)} 条：")
        for a in alerts:
            print(f"  · {a}")
    else:
        print("✅ 一切正常，无告警。")


# ---------------------------------------------------------------- 演示数据
def demo():
    # (调用名, 延迟ms, token, 是否成功) —— 故意埋一个高失败率、一个慢调用
    samples = (
        [("chat_api", 320 + i * 40, 180 + i * 30, True) for i in range(10)]
        + [("ocr_api", 500, 60, True), ("ocr_api", 800, 60, False),
           ("ocr_api", 600, 60, False), ("ocr_api", 550, 60, True),
           ("ocr_api", 700, 60, False)]
        + [("summarize", 1500, 900, True), ("summarize", 2600, 1100, True),
           ("summarize", 2200, 950, True), ("summarize", 1800, 800, True),
           ("summarize", 2400, 1000, True)]
    )
    for name, ms, tok, ok in samples:
        record_call(name, ms, tok, ok)
    render_report(aggregate(), check_alerts(aggregate()))
    print("\n提示：ocr_api 中招（成功率低）、summarize 中招（P95 超标）——"
          "改改上面 samples 里的数据，看告警怎么变化。")


def single_ask():
    """演示单次调用的采集：真实场景中 record_call 包在调用函数外层。"""
    name = "demo_call"
    t0 = time.perf_counter()
    time.sleep(0.05)  # 模拟一次模型调用的耗时
    ms = (time.perf_counter() - t0) * 1000
    tid = record_call(name, ms, 42, True)
    print(f"[采集] trace_id={tid} name={name} latency={ms:.0f}ms tokens=42 ok=True")
    render_report(aggregate(), check_alerts(aggregate()))


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "ask":
        single_ask()
    else:
        demo()


if __name__ == "__main__":
    main()
