# 常见错误：认证装饰器应该在最外层
@log_execution      # ❌ 错误：日志可能在认证失败后仍执行
@require_auth
def sensitive_api():
    pass

# 正确顺序：
@require_auth       # ✅ 正确：先认证
@log_execution      # 认证通过后才记录日志
def sensitive_api():
    pass
