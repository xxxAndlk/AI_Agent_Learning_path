# 使用dataclass定义数据结构
from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: int
    name: str
    email: Optional[str] = None
    
    def __post_init__(self):
        if self.email and '@' not in self.email:
            raise ValueError("Invalid email")

# 使用类型注解和文档字符串
def calculate_discount(
    price: float,
    discount_rate: float = 0.1,
    *,
    min_price: float = 0,
) -> float:
    """
    计算折扣后价格。
    
    Args:
        price: 原价
        discount_rate: 折扣率，默认10%
        min_price: 最低价格限制
    
    Returns:
        折扣后价格
    """
    final_price = price * (1 - discount_rate)
    return max(final_price, min_price)
