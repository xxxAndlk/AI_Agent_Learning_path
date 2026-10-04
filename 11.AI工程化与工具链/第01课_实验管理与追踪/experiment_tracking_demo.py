"""experiment_tracking_demo.py —— 最小实验追踪：把一次实验的参数/数据/结果/时间戳写进 json 并读回对比。

纯标准库，零依赖，离线真跑：python experiment_tracking_demo.py
（对应第 11 章第 01 课；12 章第 04 课监控 Dashboard 将复用"一条记录=json 一行"的思路）
"""
import hashlib
import json
import random
import time
from pathlib import Path

RUNS_DIR = Path("runs")  # 所有实验记录都摊在这里，一个实验一个 json


def fake_train(params: dict, seed: int) -> float:
    """模拟一次训练：同样的参数+种子得到同样的结果（这正是"可复现"的模拟）。"""
    rng = random.Random(seed + params["lr"] * 1000 + params["batch_size"])
    base = 0.70
    bonus = params["batch_size"] * 0.0004  # batch 稍大有微弱收益（演示用，非真实规律）
    return round(min(0.99, base + rng.random() * 0.05 + bonus), 4)


def run_experiment(note: str, **params) -> Path:
    """跑一次"实验"，把完整现场写进 json。任何字段拿不准要不要记？记。"""
    record = {
        "note": note,
        "params": params,                                   # 参数：你定的设置
        "data": {                                           # 数据：用的哪份数据
            "file": "corpus.txt",
            "fingerprint": hashlib.md5(b"v2-final").hexdigest()[:8],
            "n_items": 5120,
        },
        "seed": 42,                                         # 随机种子也是参数的一部分
        "started_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "result": None,                                     # 结果：跑完再填
    }
    print(f"[{note}] 训练中...（lr={params['lr']}, batch_size={params['batch_size']}）")
    time.sleep(0.3)
    record["result"] = {"accuracy": fake_train(params, record["seed"]), "cost_min": 0.3}

    RUNS_DIR.mkdir(exist_ok=True)
    path = RUNS_DIR / f"{time.strftime('%Y%m%d_%H%M%S')}_{note}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"  已存档 -> {path}\n  结果: {record['result']}\n")
    return path


def main() -> None:
    print("== 实验 1：基线 ==")
    p1 = run_experiment("baseline", lr=0.001, batch_size=32)

    print("== 实验 2：调参后（一次只改一个变量）==")
    p2 = run_experiment("lr_x10", lr=0.01, batch_size=32)

    print("== 读回对比：可复现的看谱方式 ==")
    rows = []
    for p in (p1, p2):
        r = json.loads(p.read_text(encoding="utf-8"))
        rows.append((r["note"], r["params"], r["data"]["fingerprint"], r["result"]["accuracy"]))
        print(f"{r['note']:<10} lr={r['params']['lr']:<6} acc={r['result']['accuracy']}"
              f"  数据指纹={r['data']['fingerprint']}  {r['started_at']}")

    best = max(rows, key=lambda x: x[3])
    print(f"\n最优: {best[0]} (acc={best[3]})。它是怎么来的？参数与数据指纹都在记录里，随时可复现。")


if __name__ == "__main__":
    main()
