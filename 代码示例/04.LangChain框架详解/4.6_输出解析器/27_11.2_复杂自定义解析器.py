"""
复杂自定义解析器：表格解析器
展示如何解析表格格式的文本输出
"""

from langchain_core.output_parsers import BaseOutputParser
from typing import List, Dict, Any
import re

class TableParser(BaseOutputParser[List[Dict[str, str]]]):
    """
    表格解析器
    解析表格形式的文本输出
    支持 Markdown 表格格式
    """
    
    def parse(self, text: str) -> List[Dict[str, str]]:
        """解析表格文本"""
        lines = text.strip().split('\n')
        
        # 找到表格开始和结束
        table_lines = []
        in_table = False
        
        for line in lines:
            line = line.strip()
            
            # 检测表格开始（包含 | 的行）
            if '|' in line and not line.startswith('|'):
                continue
            if '|' in line:
                # 跳过分割行（如 |---|）
                if re.match(r'^\|[\s\-:|]+\|$', line):
                    continue
                in_table = True
                table_lines.append(line)
            elif in_table and line:
                # 表格结束
                break
        
        if not table_lines:
            return []
        
        # 解析表头
        header_line = table_lines[0]
        headers = [h.strip() for h in header_line.split('|') if h.strip()]
        
        # 解析数据行
        result = []
        for line in table_lines[1:]:
            values = [v.strip() for v in line.split('|') if v.strip()]
            if len(values) == len(headers):
                row = dict(zip(headers, values))
                result.append(row)
        
        return result
    
    @property
    def _type(self) -> str:
        return "table"

# ============================================================
# 使用表格解析器
# ============================================================
parser = TableParser()

table_text = """
以下是学生成绩单：

| 姓名 | 语文 | 数学 | 英语 | 总分 |
|------|------|------|------|------|
| 张三 | 85   | 92   | 88   | 265  |
| 李四 | 90   | 87   | 93   | 270  |
| 王五 | 78   | 85   | 82   | 245  |
"""

result = parser.parse(table_text)

print("解析结果：")
for row in result:
    print(f"  {row}")

print(f"\n类型: {type(result)}")
print(f"记录数: {len(result)}")
