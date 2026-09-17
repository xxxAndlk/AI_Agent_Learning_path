package main

import (
	"os"
	"path/filepath"
	"runtime"
	"strconv"

	"github.com/joho/godotenv"
	"github.com/openai/openai-go"
	"github.com/openai/openai-go/option"
)

type Config struct {
	APIKey       string
	BaseURL      string
	LLMModel     string
	EmbedModel   string
	RepoRoot     string // 知识库根目录（仓库根）
	ProjectDir   string // 本项目目录
	DataDir      string // 向量库落盘目录
	Collection   string
	ChunkSize    int
	ChunkOverlap int
	TopK         int
	Concurrency  int // 向量化并发数
}

func loadConfig() Config {
	// 用 runtime.Caller 定位本项目目录，不依赖"从哪个目录执行命令"
	_, file, _, _ := runtime.Caller(0)
	projectDir := filepath.Dir(file)

	_ = godotenv.Load(filepath.Join(projectDir, ".env"))

	repoRoot := os.Getenv("KNOWLEDGE_ROOT")
	if repoRoot == "" {
		repoRoot = filepath.Dir(projectDir) // 本项目就放在仓库根目录下
	}

	return Config{
		APIKey:       os.Getenv("OPENAI_API_KEY"),
		BaseURL:      envStr("OPENAI_BASE_URL", "https://api.openai.com/v1"),
		LLMModel:     envStr("LLM_MODEL", "gpt-5.4-mini"),
		EmbedModel:   envStr("EMBEDDING_MODEL", "text-embedding-3-small"),
		RepoRoot:     repoRoot,
		ProjectDir:   projectDir,
		DataDir:      envStr("DATA_DIR", filepath.Join(projectDir, "data", "chromem_db")),
		Collection:   envStr("COLLECTION", "ai_stack_docs"),
		ChunkSize:    envInt("CHUNK_SIZE", 800),
		ChunkOverlap: envInt("CHUNK_OVERLAP", 120),
		TopK:         envInt("TOP_K", 6),
		Concurrency:  envInt("EMBED_CONCURRENCY", 8),
	}
}

// 走 OpenAI 兼容协议：换 OPENAI_BASE_URL 就能接中转网关 / Ollama / 本地 vLLM
func newLLMClient() openai.Client {
	return openai.NewClient(
		option.WithAPIKey(cfg.APIKey),
		option.WithBaseURL(cfg.BaseURL),
	)
}

func envStr(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}

func envInt(key string, def int) int {
	v := os.Getenv(key)
	if v == "" {
		return def
	}
	n, err := strconv.Atoi(v)
	if err != nil {
		return def
	}
	return n
}

var cfg = loadConfig()
