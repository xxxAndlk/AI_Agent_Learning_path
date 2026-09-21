# ============ 泛型类型 ============
from typing import TypeVar, Generic, List, Dict

# 泛型变量（类似Go的泛型 T）
T = TypeVar('T')                   # 定义泛型变量T
U = TypeVar('U')
K = TypeVar('K')
V = TypeVar('V')

# 泛型函数（类似Go的泛型函数 func Swap[T any](a, b T) (T, T)）
def first_element(items: List[T]) -> Optional[T]:
    """返回列表的第一个元素"""
    return items[0] if items else None

# 使用泛型
numbers: List[int] = [1, 2, 3]
first_num = first_element(numbers)   # 类型检查器知道返回Optional[int]

strings: List[str] = ["a", "b", "c"]
first_str = first_element(strings)   # 类型检查器知道返回Optional[str]

# 泛型类（类似Go的泛型结构体）
class Container(Generic[T]):
    """泛型容器类"""
    
    def __init__(self) -> None:
        self.items: List[T] = []
    
    def add(self, item: T) -> None:
        self.items.append(item)
    
    def get(self) -> Optional[T]:
        return self.items[0] if self.items else None
    
    def get_all(self) -> List[T]:
        return self.items

# 使用泛型类
int_container: Container[int] = Container()
int_container.add(42)
num = int_container.get()          # 类型检查器知道返回Optional[int]

str_container: Container[str] = Container()
str_container.add("hello")
text = str_container.get()         # 类型检查器知道返回Optional[str]

# 泛型字典（类似Go的 map[K]V）
def merge_dicts(d1: Dict[K, V], d2: Dict[K, V]) -> Dict[K, V]:
    """合并两个字典"""
    result = d1.copy()
    result.update(d2)
    return result

merged: Dict[str, int] = merge_dicts(
    {"a": 1, "b": 2},
    {"b": 3, "c": 4}
)  # {"a": 1, "b": 3, "c": 4}

# 多个泛型变量
def create_pair(a: T, b: U) -> Tuple[T, U]:
    """创建键值对"""
    return (a, b)

pair: Tuple[int, str] = create_pair(1, "one")
