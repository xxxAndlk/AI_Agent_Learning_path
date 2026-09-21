# ✓ 好：处理预期的异常

import json

try:
    config = json.load(open("config.json"))
except FileNotFoundError:
    config = default_config()
except json.JSONDecodeError:
    logger.error("Invalid JSON in config")
    config = default_config()

# ✗ 避免：过度捕获
try:
    do_something()
except:  # 捕获所有异常，隐藏错误
    pass

# ✓ 好：具体异常
try:
    do_something()
except (ValueError, TypeError) as e:
    logger.error(f"Error: {e}")
