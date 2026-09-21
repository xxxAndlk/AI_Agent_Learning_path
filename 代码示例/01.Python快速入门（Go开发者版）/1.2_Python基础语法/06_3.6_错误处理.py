# Python: 异常机制
try:
    risky_operation()
except SpecificError as e:
    handle_error(e)
finally:
    cleanup()

# Go: 返回值检查
# result, err := riskyOperation()
# if err != nil {
#     handleError(err)
# }
