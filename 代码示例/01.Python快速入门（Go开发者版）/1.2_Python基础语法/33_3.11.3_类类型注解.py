# Python类（带注解）
class Person:
    name: str
    age: int
    
    def greet(self) -> str:
        pass

# Go等价
# type Person struct {
#     Name string
#     Age  int
# }
#
# func (p Person) Greet() string {
#     return "你好, " + p.Name
# }
