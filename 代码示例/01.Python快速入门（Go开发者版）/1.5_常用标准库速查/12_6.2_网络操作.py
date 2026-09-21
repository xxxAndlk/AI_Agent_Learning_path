"""
网络操作示例 - 对比Go的net/http
"""

import urllib.request
import urllib.parse
import http.client

# ============ HTTP GET ============
# Go: http.Get()

url = "https://api.example.com/data"
response = urllib.request.urlopen(url)
data = response.read().decode('utf-8')

# 添加Headers
req = urllib.request.Request(
    url,
    headers={'User-Agent': 'Python App'}
)
response = urllib.request.urlopen(req)

# ============ HTTP POST ============
# Go: http.Post()

post_data = urllib.parse.urlencode({'key': 'value'}).encode()
req = urllib.request.Request(
    url,
    data=post_data,
    method='POST'
)
response = urllib.request.urlopen(req)

# ============ 更好的选择：requests库（第三方） ============
# pip install requests
# 虽然这不是标准库，但比urllib更常用

"""
import requests

response = requests.get(url, headers={'User-Agent': 'App'})
print(response.json())

response = requests.post(url, json={'key': 'value'})
"""
