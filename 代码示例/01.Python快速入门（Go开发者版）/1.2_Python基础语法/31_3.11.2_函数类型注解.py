# Python:
from typing import Any, Dict, Optional

def process(a: int, b: Optional[str] = None) -> Dict[str, Any]:
    pass

# Go:
# func Process(a int, b *string) map[string]interface{} {
#     // Go不支持默认参数，但可以用指针模拟Optional
# }
