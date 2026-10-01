"""数据处理管道 - ETL示例"""

import json
import csv
from datetime import datetime
from pathlib import Path

def extract(file_path):
    """从JSON提取数据"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def transform(data):
    """转换数据"""
    for item in data:
        item['processed_at'] = datetime.now().isoformat()
        item['upper_name'] = item['name'].upper()
    return data

def load(data, output_path):
    """加载到CSV"""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

# 运行管道
data = extract("input.json")
data = transform(data)
load(data, "output.csv")
