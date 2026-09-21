"""
带验证的自定义解析器
展示如何在解析过程中进行数据验证
"""

from langchain_core.output_parsers import BaseOutputParser
from typing import List
from pydantic import BaseModel, ValidationError

# ============================================================
# 验证模型
# ============================================================
class PersonInfo(BaseModel):
    """人物信息验证模型"""
    name: str
    age: int
    email: str
    
    def __str__(self):
        return f"{self.name}, {self.age}岁, {self.email}"

# ============================================================
# 带验证的解析器
# ============================================================
class ValidatedPersonParser(BaseOutputParser[List[PersonInfo]]):
    """
    人物信息解析器（带验证）
    解析文本中的个人信息并进行验证
    """
    
    def parse(self, text: str) -> List[PersonInfo]:
        """解析并验证人物信息"""
        result = []
        lines = text.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 尝试解析每一行（假设格式为：姓名, 年龄, 邮箱）
            parts = [p.strip() for p in line.split(',')]
            
            if len(parts) >= 3:
                try:
                    # 提取年龄（移除"岁"字）
                    age_str = parts[1].replace('岁', '')
                    age = int(age_str)
                    
                    person = PersonInfo(
                        name=parts[0],
                        age=age,
                        email=parts[2]
                    )
                    result.append(person)
                except (ValueError, ValidationError) as e:
                    # 验证失败时跳过该记录
                    print(f"跳过无效记录: {line} - {e}")
                    continue
        
        return result
    
    @property
    def _type(self) -> str:
        return "validated_person"

# ============================================================
# 使用验证解析器
# ============================================================
parser = ValidatedPersonParser()

test_text = """
张三, 30岁, zhangsan@example.com
李四, 25岁, lisi@example.com
王五, 三十二岁, wangwu@example.com  # 无效的年龄格式
赵六, 28, zhaoliu@example.com
"""

result = parser.parse(test_text)

print("验证通过的记录：")
for person in result:
    print(f"  {person}")

print(f"\n成功解析: {len(result)} 条记录")
