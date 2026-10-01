# Python泛型
def first_element[T](items: list[T]) -> T | None:
    return items[0] if items else None


# func FirstElement[T any](items []T) *T {
#     if len(items) == 0 {
#         return nil
#     }
#     return &items[0]
# }
