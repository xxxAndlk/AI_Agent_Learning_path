# report.py —— 第 11 课课上程序：月度消费小报告
# 本课主角全部出场：推导式、生成器表达式、datetime、json、pathlib
from datetime import datetime
from pathlib import Path
import json
import tempfile

# 内置的月度消费记录：列表套字典，第 10 课购物车也是这个路数
records = [
    {"category": "餐饮", "item": "早餐煎饼", "amount": 9},
    {"category": "交通", "item": "地铁通勤卡", "amount": 30},
    {"category": "餐饮", "item": "工作日午餐", "amount": 25},
    {"category": "购物", "item": "秋季外套", "amount": 199},
    {"category": "娱乐", "item": "电影票", "amount": 45},
    {"category": "餐饮", "item": "周末聚餐", "amount": 168},
    {"category": "购物", "item": "数据线", "amount": 29},
    {"category": "娱乐", "item": "游戏月卡", "amount": 30},
]

BIG = 100  # 单笔超过这个数算"大额"

month = input("生成哪个月的报告？（直接回车 = 本月）").strip()
if not month:
    # strftime 把当前时间按格式变成字符串，%m 是两位数月份
    month = datetime.now().strftime("%Y年%m月")

# 集合推导式：出现过哪些分类（顺便去重）；sorted 让每次打印顺序一致
categories = sorted({r["category"] for r in records})

# 字典推导式：每个分类的花销。sum() 括号里是生成器表达式——
# 不必先造一个"餐饮的所有金额"列表，逐条看、合格就加，省内存
totals = {c: sum(r["amount"] for r in records if r["category"] == c) for c in categories}

big_deals = [r for r in records if r["amount"] >= BIG]  # 带筛选的推导式
grand_total = sum(r["amount"] for r in records)

# ---- 打印报告 ----
now = datetime.now()
print("=" * 36)
print(f"  {month} 消费小报告")
print(f"  生成时间：{now.strftime('%Y-%m-%d %H:%M')}")
print("=" * 36)
print(f"共 {len(records)} 笔，合计 {grand_total} 元。分类小计：")
for c, t in totals.items():  # 字典可以直接遍历，一对一对拿
    # 分类都是两个字，后面补两个全角空格正好上下对齐
    print(f"  {c}　　{t:>6.2f} 元")
print("-" * 36)
print(f"单笔超过 {BIG} 元的大额（共 {len(big_deals)} 笔）：")
for r in big_deals:
    print(f"  - {r['item']}：{r['amount']} 元（{r['category']}）")

# ---- 存成 JSON 再读回确认（写进系统临时文件夹，课目录不留数据文件）----
summary = {
    "month": month,
    "generated_at": now.strftime("%Y-%m-%d %H:%M:%S"),
    "count": len(records),
    "total": grand_total,
    "by_category": totals,
}
# Path 用 / 拼路径；tempfile.gettempdir() 是系统临时文件夹
summary_path = Path(tempfile.gettempdir()) / "python_lesson11_summary.json"
with open(summary_path, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

with open(summary_path, "r", encoding="utf-8") as f:
    saved = json.load(f)

print("-" * 36)
print(f"汇总已写入 {summary_path.name} 并读回确认：")
print(f"  {saved['month']} 共 {saved['count']} 笔，合计 {saved['total']} 元")
