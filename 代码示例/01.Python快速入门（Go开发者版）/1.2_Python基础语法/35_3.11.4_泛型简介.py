# Python泛型
def first_element[T](items: list[T]) -> T | None:
    return items[0] if items else None

# Go等价（Python 3.12+可以使用更简洁的语法）
# func FirstElement[T any](items []T) *T {
#     if len(items) == 0 {
#         return nil
#     }
#     return &items[0]
# }
