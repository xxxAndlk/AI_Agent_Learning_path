# 带类型注解时，IDE知道person.greet()返回str
person = Person("张三", 25)
person.greet().upper()  # IDE能提示upper()方法
