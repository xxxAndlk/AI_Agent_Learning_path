// Go的编码解码
import (
    "encoding/base64"
    "encoding/hex"
    "hash/crc32"
)

// Base64
encoded := base64.StdEncoding.EncodeToString([]byte(data))
decoded, _ := base64.StdEncoding.DecodeString(encoded)

// URL安全Base64
urlEncoded := base64.URLEncoding.EncodeToString([]byte(data))

// Hex
hexEncoded := hex.EncodeToString([]byte(data))

// CRC32
crc32Hash := crc32.New(crc32.IEEE)
crc32Hash.Write([]byte(data))
crc := crc32Hash.Sum32()
