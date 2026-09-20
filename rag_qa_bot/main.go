package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"math"
	"net/http"
	"os"
)

// ========== 1. 文本切片 ==========

// ============================================
// 1. 文本切片函数
// ============================================

// splitText 将长文本按固定长度切分成多个小块
// chunkSize: 每个块的最大字符数（按 rune 计算，支持中文）
// overlap:   相邻块之间重叠的字符数，保证上下文不丢失
func splitText(text string, chunkSize int, overlap int) []string {
	// 将字符串转为 rune 切片，确保中文字符不会被截断
	runes := []rune(text)
	var chunks []string

	// 步长 = chunkSize - overlap，实现滑动窗口效果
	for i := 0; i < len(runes); i += chunkSize - overlap {
		end := i + chunkSize
		if end > len(runes) {
			end = len(runes) // 最后一块可能不足 chunkSize
		}
		chunks = append(chunks, string(runes[i:end]))
		if end == len(runes) {
			break // 已到达文本末尾，结束循环
		}
	}
	return chunks
}

// ============================================
// 2. Embedding 调用（从 main 中提取复用）
// ============================================

// getEmbedding 调用本地 Ollama 服务，将任意文本转为向量
// 返回 768 维的 float64 切片（bge-m3 模型）
func getEmbedding(text string) ([]float64, error) {
	// 构造请求体，Ollama /api/embeddings 接口使用 prompt 字段传文本
	reqBody := EmbedRequest{
		Model: "bge-m3",
		Input: text,
	}
	jsonData, _ := json.Marshal(reqBody)

	// 发送 HTTP POST 请求到本地 Ollama 服务
	resp, err := http.Post(
		"http://localhost:11434/api/embeddings",
		"application/json",
		bytes.NewBuffer(jsonData),
	)
	if err != nil {
		return nil, err // 网络错误直接返回
	}
	defer resp.Body.Close()

	// 读取响应体并解析 JSON
	body, _ := io.ReadAll(resp.Body)
	var result EmbedResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, err
	}
	return result.Embedding, nil
}

// ============================================
// 3. 向量相似度计算
// ============================================

// cosineSimilarity 计算两个向量的余弦相似度
// 值域 [-1, 1]，值越大表示语义越接近
// 公式: (A·B) / (|A| * |B|)
func cosineSimilarity(a, b []float64) float64 {
	var dotProduct float64 // 向量点积 A·B
	var normA float64      // 向量 A 的模长平方和
	var normB float64      // 向量 B 的模长平方和

	for i := range a {
		dotProduct += float64(a[i]) * float64(b[i])
		normA += float64(a[i]) * float64(a[i])
		normB += float64(b[i]) * float64(b[i])
	}

	// 处理零向量情况，避免除零错误
	if normA == 0 || normB == 0 {
		return 0
	}

	// 返回余弦相似度
	return dotProduct / (math.Sqrt(normA) * math.Sqrt(normB))
}

type EmbedRequest struct {
	Model string `json:"model"`
	Input string `json:"prompt"` // Ollama 的 embeddings API 用 prompt 字段
}

type EmbedResponse struct {
	Embedding []float64 `json:"embedding"`
}

// ========== 数据结构 ==========

// Chunk 代表一个文本切片及其向量
type Chunk struct {
	Text      string    // 原始文本
	Embedding []float64 // 向量
}

// 分片大小，重叠词数
var chhunkSize, overlap = 80, 20

func main() {
	// ============================================
	// 4.1 读取本地 Markdown 文档
	// ============================================
	// 读取 knowledge.md 文件全部内容到内存
	data, err := os.ReadFile("knowledge.md")
	if err != nil {
		panic(err) // 文件不存在则直接报错退出
	}
	text := string(data)

	// ============================================
	// 4.2 文本切片
	// ============================================
	// 每片 80 个字符，相邻两片重叠 20 个字符
	// 重叠的目的是防止关键信息正好落在切片边界上
	chunks := splitText(text, chhunkSize, overlap)
	fmt.Printf("📄 文档共 %d 字，切出 %d 片\n\n", len([]rune(text)), len(chunks))

	// ============================================
	// 4.3 向量化并建立内存向量库
	// ============================================
	var store []Chunk // 内存向量库，用切片存储所有 Chunk

	for i, c := range chunks {
		fmt.Printf("🔹 处理第 %d/%d 片... ", i+1, len(chunks))
		// 调用 Ollama 将当前文本块转为向量
		emb, err := getEmbedding(c)
		if err != nil {
			fmt.Printf("❌ 失败: %v\n", err)
			continue // 跳过失败的块，继续处理下一个
		}
		// 存入内存向量库
		store = append(store, Chunk{Text: c, Embedding: emb})
		fmt.Printf("✓ 向量维度 %d\n", len(emb))
	}
	fmt.Printf("\n💾 内存向量库建立完成，共 %d 条记录\n\n", len(store))

	// ============================================
	// 4.4 检索测试：输入问题，找出最相关的文本块
	// ============================================
	query := "goroutine 和线程有什么区别"
	fmt.Printf("🔍 用户查询: %s\n\n", query)

	// 将查询问题也转为向量（只有同维向量才能比较相似度）
	queryEmb, err := getEmbedding(query)
	if err != nil {
		panic(err)
	}

	// ============================================
	// 4.5 计算相似度并排序
	// ============================================
	// 定义内部结构用于存储检索结果
	type searchResult struct {
		text       string  // 文本内容
		similarity float64 // 与查询的余弦相似度
	}
	var results []searchResult

	// 遍历向量库中所有记录，逐个计算与查询的相似度
	for _, chunk := range store {
		sim := cosineSimilarity(queryEmb, chunk.Embedding)
		results = append(results, searchResult{
			text:       chunk.Text,
			similarity: sim,
		})
	}

	// 冒泡排序：按相似度从高到低排列
	// 生产环境可用 sort.Slice，这里用简单实现方便理解原理
	for i := 0; i < len(results); i++ {
		for j := i + 1; j < len(results); j++ {
			if results[j].similarity > results[i].similarity {
				results[i], results[j] = results[j], results[i]
			}
		}
	}

	// ============================================
	// 4.6 输出 Top-3 最相关结果
	// ============================================
	fmt.Println("=== 最相关的 3 片 ===")
	for i := 0; i < 3 && i < len(results); i++ {
		fmt.Printf("\n[相似度 %.4f]\n%s\n", results[i].similarity, results[i].text)
	}
}
