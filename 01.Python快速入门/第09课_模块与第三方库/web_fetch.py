# 本课开始用第三方库。运行前先装 requests（建议在虚拟环境里装）：
#   pip install requests

import requests

url = input("请输入要访问的网址（比如 https://www.python.org ）：")

# timeout=10：最多等 10 秒。不写 timeout 的话，对方服务器卡住时程序会一直傻等下去
try:
    response = requests.get(url, timeout=10)
    print("状态码：", response.status_code)
    # 200 表示一切正常；404 表示页面不存在；别的号遇到了再查
    print("页面开头是：")
    print(response.text[:200])
except requests.exceptions.RequestException as error:
    # 断网、网址写错、超时……都归这一类异常接住，程序不会崩出一屏红字
    print("访问失败了：", error)
    print("先检查网络连上没有，再看网址拼写有没有错。")
