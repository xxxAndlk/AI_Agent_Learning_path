# ============ 错误处理 ============
# 其他语言的风格：if err != nil
# Python的风格：try/except/else/finally

# if err != nil {
#     log.Fatal(err)
# }
# defer file.Close()

# 
try:
    # 可能出错的代码
    file = open("test.txt", "r")
    content = file.read()
    
except FileNotFoundError as e:      # 捕获特定异常
    print(f"文件未找到: {e}")
    
except PermissionError:
    print("没有权限读取文件")
    
except Exception as e:              # 捕获所有异常
    print(f"发生错误: {e}")
    
else:
    # 没有异常时执行
    print(f"文件内容: {content}")
    
finally:
    # 无论是否异常都执行
    if 'file' in locals() and not file.closed:
        file.close()
        print("文件已关闭")

# Python的with语句
# 自动管理资源，确保关闭
# if err != nil {
#     return err
# }
# defer file.Close()

# 
try:
    with open("test.txt", "r") as file:     # 自动关闭
        content = file.read()
        print(content)
except FileNotFoundError:
    print("文件不存在")

# 自定义异常
class ValidationError(Exception):
    """验证错误"""
    pass

def validate_age(age):
    if age < 0 or age > 150:
        raise ValidationError(f"无效的年龄: {age}")
    return True

import os
