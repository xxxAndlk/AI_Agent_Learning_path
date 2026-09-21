# ============ 状态机实现（对比Go的select） ============
# Go用select处理多个channel，Python用生成器模拟状态机

def state_machine():
    """简单状态机：接收命令切换状态"""
    state = "idle"
    while True:
        event = yield f"状态: {state}"
        
        if state == "idle":
            if event == "start":
                state = "running"
        elif state == "running":
            if event == "pause":
                state = "paused"
            elif event == "stop":
                state = "idle"
        elif state == "paused":
            if event == "resume":
                state = "running"
            elif event == "stop":
                state = "idle"

# 使用状态机
sm = state_machine()
print(next(sm))       # 状态: idle
print(sm.send("start"))   # 状态: running
print(sm.send("pause"))   # 状态: paused
print(sm.send("resume"))  # 状态: running
print(sm.send("stop"))    # 状态: idle
