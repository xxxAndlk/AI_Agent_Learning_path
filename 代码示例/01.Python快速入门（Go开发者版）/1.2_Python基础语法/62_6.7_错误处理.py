# ============ 错误处理（对比Go） ============
# Go的风格：if err != nil
# Python的风格：try/except/else/finally

# Go:
# file, err := os.Open("test.txt")
# if err != nil {
#     log.Fatal(err)
# }
# defer file.Close()

# Python:
try:
    # 可能出错的代码
    file = open("test.txt", "r")
    content = file.read()
    
except FileNotFoundError as e:      # 捕获特定异常（类似Go的类型断言）
    print(f"文件未找到: {e}")
    
except PermissionError:
    print("没有权限读取文件")
    
except Exception as e:              # 捕获所有异常（类似Go的catch-all）
    print(f"发生错误: {e}")
    
else:
    # 没有异常时执行（Go没有直接对应）
    print(f"文件内容: {content}")
    
finally:
    # 无论是否异常都执行（类似Go的defer）
    if 'file' in locals() and not file.closed:
        file.close()
        print("文件已关闭")

# Python的with语句（类似Go的defer，但更简洁）
# 自动管理资源，确保关闭
# Go:
# file, err := os.Open("test.txt")
# if err != nil {
#     return err
# }
# defer file.Close()

# Python:
try:
    with open("test.txt", "r") as file:     # 自动关闭
        content = file.read()
        print(content)
except FileNotFoundError:
    print("文件不存在")

# 自定义异常（类似Go的自定义error类型）
class ValidationError(Exception):
    """验证错误"""
    pass

def validate_age(age):
    if age < 0 or age > 150:
        raise ValidationError(f"无效的年龄: {age}")
    return True

import os
