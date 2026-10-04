# -*- coding: utf-8 -*-
"""feature_demo.py —— 用纯标准库演示特征工程两步：
手工打分做特征选择（剔除添乱列）+ 从原始字段提取简单新特征。pandas 对照段需先安装：pip install pandas"""

# ---------------- 一份"用户流失预测"小表（原始形态） ----------------
RAW = [
    {"user_id": "u001", "phone_tail": "5521", "order_count": 12, "days_since_login": 3,  "city": "上海", "churned": 0},
    {"user_id": "u002", "phone_tail": "8807", "order_count": 1,  "days_since_login": 90, "city": "北京", "churned": 1},
    {"user_id": "u003", "phone_tail": "3312", "order_count": 5,  "days_since_login": 30, "city": "上海", "churned": 1},
    {"user_id": "u004", "phone_tail": "9948", "order_count": 30, "days_since_login": 1,  "city": "广州", "churned": 0},
    {"user_id": "u005", "phone_tail": "1170", "order_count": 2,  "days_since_login": 60, "city": "北京", "churned": 1},
    {"user_id": "u006", "phone_tail": "6629", "order_count": 18, "days_since_login": 5,  "city": "上海", "churned": 0},
]

# 手工打分：相关吗(0~2) / 数据完整吗(0~1) / 好算吗(0~1)；总分>=3 才留
SCORE_TABLE = [
    ("user_id",         "仅是编号，和流不流失无关",            0, 1, 1),
    ("phone_tail",      "手机尾号和任何目标都无关，纯添乱",     0, 1, 1),
    ("order_count",     "下单少的人更容易流失，强相关",         2, 1, 1),
    ("days_since_login","越久没登录越可能流失，强相关",         2, 1, 1),
    ("city",            "不同城市流失率可能不同，弱相关",       1, 1, 1),
]

# ---------------- 特征选择：打分 + 剔除 ----------------
def select_features():
    print("== 手工打分（相关/完整/好算，满分4，>=3留用）==")
    keep = []
    for name, why, rel, ok, easy in SCORE_TABLE:
        total = rel + ok + easy
        verdict = "留用" if total >= 3 else "剔除"
        keep.append((name, verdict == "留用"))
        print(f"  {name:<18} 相关{rel} 完整{ok} 好算{easy} 总分{total} -> {verdict}（{why}）")

    print("\n== 特征提取：从原始字段造新特征 ==")
    for r in RAW:
        # 新特征1：低频用户（订单<3）；新特征2：城市一行多列编码
        r["is_low_freq"] = 1 if r["order_count"] < 3 else 0
        r["city_上海"], r["city_北京"] = (1, 0) if r["city"] == "上海" else (0, 1) if r["city"] == "北京" else (0, 0)
    return keep


def preview(keep):
    chosen = [n for n, ok in keep if ok] + ["is_low_freq", "city_上海", "city_北京"]
    print("\n== 最终特征向量（模型吃的就是这个）==")
    for r in RAW:
        vec = [r[n] for n in chosen]
        print(f"  {r['user_id']} -> {vec}  目标(churned)={r['churned']}")
    print(f"\n留下特征：{chosen}")
    print("剔除特征：" + ", ".join(n for n, ok in keep if not ok))


if __name__ == "__main__":
    keep = select_features()
    preview(keep)

    # ---------------- pandas 对照段（可选） ----------------
    try:
        import pandas as pd
    except ImportError:
        print("\n[跳过] 未安装 pandas（pip install pandas），对照段略过；上面纯标准库版已完整演示。")
    else:
        df = pd.DataFrame(RAW)
        print("\n== pandas 对照（改列名/查相关性）==")
        df = df.drop(columns=["user_id", "phone_tail"])           # 剔除添乱列
        print(df[["order_count", "days_since_login", "churned"]].corr().round(2))
        print("（相关系数接近 0 的列，通常就是打分时'相关'项拿低分的列）")
