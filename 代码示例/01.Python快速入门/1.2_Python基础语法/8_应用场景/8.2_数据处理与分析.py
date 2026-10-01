import csv
from collections import defaultdict

def analyze_sales_data(csv_file):
    """分析销售数据"""
    monthly_sales = defaultdict(list)
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            month = row['date'][:7]  # YYYY-MM
            sales = float(row['amount'])
            monthly_sales[month].append(sales)
    
    # 计算每月统计
    for month, sales in monthly_sales.items():
        avg = sum(sales) / len(sales)
        max_sale = max(sales)
        min_sale = min(sales)
        print(f"{month}: 平均{avg:.2f}, 最高{max_sale}, 最低{min_sale}")

# 使用列表推导式快速过滤
numbers = [1, -2, 3, -4, 5, -6]
positives = [n for n in numbers if n > 0]
squares = {n: n**2 for n in range(10)}
