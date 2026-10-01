# 练习 3 参考答案：访问一个真实网址，容错处理。
# 运行前先装第三方库（建议在虚拟环境里）：
#   pip install requests

import requests

url = "https://www.python.org"

try:
    response = requests.get(url, timeout=10)
    if response.status_code == 200:
        print("访问成功！页面开头是：")
        print(response.text[:100])
    else:
        # 网络是通的，但对方说这个页面有问题（比如 404 找不到）
        print("连上了，但状态码是", response.status_code)
except requests.exceptions.RequestException as error:
    # 断网、超时这类网络问题都归它管，程序不会崩
    print("访问失败：", error)
