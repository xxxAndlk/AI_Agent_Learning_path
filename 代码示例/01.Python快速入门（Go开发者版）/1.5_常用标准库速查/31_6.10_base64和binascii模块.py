"""
编码解码 - 对比Go的encoding/base64和encoding/hex
"""

import base64
import binascii
import urllib.parse

# ============ base64编码 ============
# Go: encoding/base64包

# 编码字符串
# Go: base64.StdEncoding.EncodeToString()
original = "Hello, World! 你好世界"
encoded = base64.b64encode(original.encode('utf-8')).decode('ascii')
print(f"Base64编码: {encoded}")  # SGVsbG8sIFdvcmxkIOesk4XNoQ==

# 解码
# Go: base64.StdEncoding.DecodeString()
decoded = base64.b64decode(encoded).decode('utf-8')
print(f"Base64解码: {decoded}")

# URL安全的Base64（替换+和/为-和_）
url_data = b"https://example.com/path?a=1&b=2"
url_encoded = base64.urlsafe_b64encode(url_data).decode('ascii')
print(f"URL安全编码: {url_encoded}")  # aHR0cHM6Ly9leGFtcGxlLmNvbS9wYXRoP2E9MSZiPTI=

url_decoded = base64.urlsafe_b64decode(url_encoded).decode('utf-8')

# 标准Base64（带填充）
std_encoded = base64.standard_b64encode(url_data)
print(f"标准编码: {std_encoded}")  # aHR0cHM6Ly9leGFtcGxlLmNvbS9wYXRoP2E9MSZiPTI=

# 编码原始字节
binary_data = b"\x00\x01\x02\xff\xfe\xfd"
b64_binary = base64.b64encode(binary_data).decode('ascii')
print(f"二进制Base64: {b64_binary}")

# ============ Base32编码 ============
# Go: encoding/base32包

original = "Hello"
encoded32 = base64.b32encode(original.encode()).decode()
print(f"Base32编码: {encoded32}")  # JBSWY3DPEHPW3PXP
decoded32 = base64.b32decode(encoded32).decode()

# ============ Base16（Hex）编码 ============
# Go: encoding/hex包

original = "Hello"
encoded16 = base64.b16encode(original.encode()).decode()
print(f"Base16编码: {encoded16}")  # 48656C6C6F
decoded16 = base64.b16decode(encoded16).decode()

# ============ binascii模块 ============
# Go: encoding/hex包

# 十六进制编码
# Go: hex.Encode()
data = b"Hello"
hex_encoded = binascii.hexlify(data).decode('ascii')
print(f"Hex编码: {hex_encoded}")  # 48656c6c6f

# 十六进制解码
# Go: hex.Decode()
decoded = binascii.unhexlify(hex_encoded)
print(f"Hex解码: {decoded}")  # b'Hello'

# 二进制和ASCII互转
# Go: strconv.ParseInt() / fmt.Sprintf()

# 将字节转换为可打印ASCII
# a2b = "ASCII to binary", b2a = "binary to ASCII"
binary_string = binascii.a2b_uu(b"Hello")
print(f"UU编码: {binary_string}")

# ============ 实际应用场景 ============

# 场景1：API认证中的Basic Auth
def generate_basic_auth(username, password):
    """生成Basic Auth头部值"""
    import base64
    credentials = f"{username}:{password}"
    encoded = base64.b64encode(credentials.encode()).decode()
    return f"Basic {encoded}"

auth_header = generate_basic_auth("admin", "password123")
print(f"Auth头: {auth_header}")

# 场景2：URL参数编码
def encode_url_token(data):
    """URL安全编码token"""
    import base64
    import urllib.parse
    # 先Base64编码，再URL编码
    b64 = base64.urlsafe_b64encode(data.encode()).decode()
    return urllib.parse.quote(b64)

def decode_url_token(encoded):
    """解码token"""
    import base64
    import urllib.parse
    b64 = urllib.parse.unquote(encoded)
    return base64.urlsafe_b64decode(b64).decode()

token = encode_url_token('{"user_id": 123}')
print(f"Token: {token}")
print(f"Decoded: {decode_url_token(token)}")

# 场景3：二进制数据传输（如WebSocket Binary）
import base64

# 模拟二进制数据
binary_data = bytes(range(256))  # 0-255

# Base64编码后传输
encoded = base64.b64encode(binary_data).decode()
print(f"编码后长度: {len(encoded)}")  # 344

# 接收端解码
decoded = base64.b64decode(encoded)
print(f"解码后长度: {len(decoded)}")  # 256

# 场景4：数据校验（CRC）
# Go: hash/crc32

# 计算CRC32
data = b"Hello, World!"
crc = binascii.crc32(data)
print(f"CRC32: {crc:#x}")  # 0x9c3b0d2c

# ============ 大文件流式编码 ============
# Go: NewEncoder() / NewDecoder()

def base64_encode_stream(input_file, output_file):
    """流式Base64编码（内存友好）"""
    with open(input_file, 'rb') as fin:
        with open(output_file, 'w') as fout:
            # 分块读取和编码
            while True:
                chunk = fin.read(3 * 1024)  # 3KB块（Base64要求3的倍数）
                if not chunk:
                    break
                encoded = base64.b64encode(chunk).decode()
                fout.write(encoded)

def base64_decode_stream(input_file, output_file):
    """流式Base64解码"""
    with open(input_file, 'r') as fin:
        with open(output_file, 'wb') as fout:
            # 一次读取多行（每行是Base64编码的块）
            while True:
                chunk = fin.read(4 * 1024)  # 4KB块
                if not chunk:
                    break
                decoded = base64.b64decode(chunk)
                fout.write(decoded)
