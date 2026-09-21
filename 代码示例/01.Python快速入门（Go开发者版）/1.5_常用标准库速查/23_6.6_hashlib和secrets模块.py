"""
加密和哈希 - 对比Go的crypto包
"""

import hashlib
import hmac
import secrets
import base64

# ============ 哈希算法 ============
# Go: crypto/sha256, crypto/md5

# MD5（不安全，仅用于兼容性）
# Go: crypto/md5
data = b"Hello, World!"
md5_hash = hashlib.md5(data).hexdigest()
print(f"MD5: {md5_hash}")  # 65a8e27d8879283831b664bd8b7f0ad4

# SHA-256（推荐）
# Go: crypto/sha256
sha256_hash = hashlib.sha256(data).hexdigest()
print(f"SHA-256: {sha256_hash}")

# SHA-512
sha512_hash = hashlib.sha512(data).hexdigest()

# 支持增量计算（处理大文件）
# Go: sha256.New()
hasher = hashlib.sha256()
hasher.update(b"Hello")
hasher.update(b", ")
hasher.update(b"World!")
result = hasher.hexdigest()

# ============ HMAC（带密钥的哈希）============
# Go: hmac.New()

key = b"secret_key"
message = "需要认证的消息".encode("utf-8")  # hmac需要bytes，中文内容显式编码

# HMAC-SHA256
hmac_result = hmac.new(key, message, hashlib.sha256).hexdigest()
print(f"HMAC-SHA256: {hmac_result}")

# 快速比较（防止时序攻击）
# Go: subtle.ConstantTimeCompare()
def secure_compare(a, b):
    """常量时间比较，防止时序攻击"""
    return hmac.compare_digest(a, b)

# ============ secrets模块（Python 3.6+）============
# Go: crypto/rand

# 生成安全随机数
# Go: rand.Reader
random_bytes = secrets.token_bytes(16)  # 16字节随机数据
random_hex = secrets.token_hex(16)      # 十六进制字符串
random_url = secrets.token_urlsafe(16)  # URL安全随机字符串

# 生成随机token用于认证
token = secrets.token_urlsafe(32)
print(f"Secure token: {token}")

# 随机整数（指定范围）
# Go: rand.Intn()
random_int = secrets.randbelow(100)  # 0-99的随机整数
print(f"Random int: {random_int}")

# ============ 密码哈希（推荐使用）============
# Go: golang.org/x/crypto/bcrypt

# 使用hashlib进行简单密码哈希（生产环境推荐bcrypt）
import hashlib

def hash_password(password, salt=None):
    """简单密码哈希（仅示例，生产环境用bcrypt）"""
    if salt is None:
        salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000  # 迭代次数
    )
    return f"{salt}${pwd_hash.hex()}"

def verify_password(password, stored):
    """验证密码"""
    salt, pwd_hash = stored.split('$')
    new_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode(),
        salt.encode(),
        100000
    )
    return hmac.compare_digest(pwd_hash, new_hash.hex())

# 使用示例
hashed = hash_password("mypassword")
print(f"Hashed: {hashed}")
print(f"Valid: {verify_password('mypassword', hashed)}")
