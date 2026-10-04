# -*- coding: utf-8 -*-
"""cleaning_demo.py —— 用纯标准库在一份"故意弄脏"的小表上演示清洗四板斧：
去重 / 填缺失 / 揪异常 / 统一格式。pandas 对照段需先安装：pip install pandas"""

# ---------------- 故意弄脏的原始数据（list[dict]） ----------------
DIRTY = [
    {"name": "张三",  "age": 28,  "city": "北京",    "signup": "2026-01-05"},
    {"name": "李四 ", "age": None, "city": "上海",    "signup": "2026/01/06"},  # 姓名带空格+年龄缺失+日期斜杠
    {"name": "张三",  "age": 28,  "city": "北京",    "signup": "2026-01-05"},   # 与第1行完全重复
    {"name": "王五",  "age": 999, "city": "beijing", "signup": "05-01-2026"},   # 年龄异常+城市英文+日期倒置
    {"name": "赵六",  "age": 34,  "city": "  上海 ", "signup": "2026-01-08"},   # 城市两头多空格
    {"name": "孙七",  "age": 22,  "city": None,      "signup": "2026-01-08"},   # 城市缺失
]

CITY_MAP = {"beijing": "北京", "shanghai": "上海", "bj": "北京", "sh": "上海"}


def show(title, rows):
    print(f"\n== {title}（{len(rows)} 行）==")
    for r in rows:
        print("  ", r)


def dedup(rows):
    """去重：整行字段拼成元组当'指纹'，第二次见到就扔。"""
    seen, out = set(), []
    for r in rows:
        key = tuple(sorted(r.items()))
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out


def fill_missing(rows):
    """填缺失：数字列用平均数（只用没缺的行算），类别列填'未知'。"""
    # 平均数只用"没缺又不离谱"的行算：999 这类笔误若参与，会把填充值带到 270+
    ages = [r["age"] for r in rows if r["age"] is not None and 0 <= r["age"] <= 120]
    avg_age = round(sum(ages) / len(ages), 1)
    out = []
    for r in rows:
        r = dict(r)  # 复制一份再改，原始数据不动（先备份的行规）
        if r["age"] is None:
            r["age"] = avg_age
        if r["city"] is None:
            r["city"] = "未知"
        out.append(r)
    return out, avg_age


def find_outliers(rows, col="age", lo=0, hi=120):
    """揪异常：最朴素的常识区间法；真项目常用 IQR 等统计法，道理相同——先划范围再逐条过目。"""
    bad = [r for r in rows if r[col] is not None and not (lo <= r[col] <= hi)]
    for r in bad:
        print(f"  [异常] {r['name']} 的 {col}={r[col]}，超出合理区间 {lo}~{hi}，记录待人工确认")
    return [r for r in rows if r not in bad]


def normalize(rows):
    """统一格式：去空格、城市英文转中文、日期归一成 YYYY-MM-DD。"""
    out = []
    for r in rows:
        r = dict(r)
        r["name"] = r["name"].strip()
        city = r["city"].strip()
        r["city"] = CITY_MAP.get(city.lower(), city)
        p = r["signup"].replace("/", "-").split("-")
        if len(p[0]) == 4:            # 2026-01-05
            y, m, d = p
        elif len(p[2]) == 4:          # 05-01-2026（美式 月-日-年）
            m, d, y = p
        else:                         # 认不出的先占位，留给人看
            y, m, d = "0000", "00", "00"
        r["signup"] = f"{y}-{m.zfill(2)}-{d.zfill(2)}"
        out.append(r)
    return out


if __name__ == "__main__":
    show("原始脏数据", DIRTY)

    rows = dedup(DIRTY)
    show("第1板斧·去重后", rows)

    rows, avg_age = fill_missing(rows)
    print(f"\n  [缺失] 年龄平均数 {avg_age}（由未缺失行算出）已用于填充；城市缺失填'未知'")
    show("第2板斧·填缺失后", rows)

    print("\n== 第3板斧·揪异常 ==")
    rows = find_outliers(rows)

    rows = normalize(rows)
    show("第4板斧·统一格式后", rows)

    # ---------------- pandas 对照段（可选） ----------------
    try:
        import pandas as pd
    except ImportError:
        print("\n[跳过] 未安装 pandas（pip install pandas），对照段略过；上面纯标准库版已完整演示。")
    else:
        df = pd.DataFrame(DIRTY)
        print("\n== pandas 对照（同样四件事）==")
        df = df.drop_duplicates()                          # 去重
        df["age"] = df["age"].fillna(df["age"].mean())     # 填缺失
        df = df[df["age"].between(0, 120)]                 # 揪异常（区间过滤）
        df["city"] = df["city"].str.strip().str.lower().map(
            lambda c: CITY_MAP.get(c, c))                  # 统一城市
        # 注：mixed 格式对 05-01-2026 这类歧义日期可能按美式解析，此处仅演示统一写法
        df["signup"] = pd.to_datetime(df["signup"], errors="coerce", format="mixed")
        print(df.to_string(index=False))
