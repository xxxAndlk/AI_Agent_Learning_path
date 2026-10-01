# 异常机制
try:
    risky_operation()
except SpecificError as e:
    handle_error(e)
finally:
    cleanup()

# if err != nil {
#     handleError(err)
# }
