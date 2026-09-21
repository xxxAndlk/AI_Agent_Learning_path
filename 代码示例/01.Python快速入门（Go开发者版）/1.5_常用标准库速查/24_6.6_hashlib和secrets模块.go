// Go的crypto包实现
import (
    "crypto/md5"
    "crypto/sha256"
    "crypto/hmac"
    "crypto/rand"
    "golang.org/x/crypto/bcrypt"
)

// 哈希
data := []byte("Hello")
sha256 := sha256.Sum256(data)

// HMAC
mac := hmac.New(sha256.New, key)
mac.Write(message)
result := mac.Sum(nil)

// 随机数
randomBytes := make([]byte, 16)
rand.Read(randomBytes)

// 密码哈希
hashed, _ := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
