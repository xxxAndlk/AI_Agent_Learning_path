"""
执行系统命令 - 对比Go的os/exec
"""

import subprocess
import shlex

# ============ 简单执行 ============
# Go: exec.Command().Output()

result = subprocess.run(
    ["ls", "-la"],
    capture_output=True,
    text=True
)
print(result.stdout)
print(result.returncode)

# ============ 安全执行（避免shell注入）============
# Go: exec.Command() with separate args

cmd = "ls"
args = ["-la", "/home"]
result = subprocess.run([cmd] + args, capture_output=True, text=True)

# ============ 管道操作 ============
# Go: cmd1 | cmd2

p1 = subprocess.Popen(["ls", "-la"], stdout=subprocess.PIPE)
p2 = subprocess.Popen(["grep", "py"], stdin=p1.stdout, stdout=subprocess.PIPE)
p1.stdout.close()
output = p2.communicate()[0]

# ============ 超时控制 ============
# Go: context.WithTimeout()

try:
    result = subprocess.run(
        ["sleep", "10"],
        timeout=5,  # 5秒超时
        capture_output=True
    )
except subprocess.TimeoutExpired:
    print("命令超时")
