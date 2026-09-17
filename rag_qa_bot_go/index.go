package main

import (
	"context"
	"errors"
	"fmt"
	"os"
	"time"

	"github.com/philippgille/chromem-go"
)

// chromem 自带的 OpenAI 兼容 Embedding 函数：同一个 .env 换 base_url 就能接 Ollama / 中转网关
func embeddingFunc() chromem.EmbeddingFunc {
	return chromem.NewEmbeddingFuncOpenAICompat(cfg.BaseURL, cfg.APIKey, cfg.EmbedModel, nil)
}

func openDB() (*chromem.DB, error) {
	if err := os.MkdirAll(cfg.DataDir, 0o755); err != nil {
		return nil, err
	}
	return chromem.NewPersistentDB(cfg.DataDir, false)
}

func openCollection() (*chromem.Collection, error) {
	db, err := openDB()
	if err != nil {
		return nil, err
	}
	return db.GetOrCreateCollection(cfg.Collection, nil, embeddingFunc())
}

func buildIndex(rebuild bool) error {
	if cfg.APIKey == "" {
		return errors.New("缺少 OPENAI_API_KEY（写进 .env 或设为环境变量）")
	}
	if rebuild {
		if err := os.RemoveAll(cfg.DataDir); err != nil {
			return err
		}
		fmt.Println("已删除旧索引，开始重建")
	}

	col, err := openCollection()
	if err != nil {
		return err
	}
	if !rebuild && col.Count() > 0 {
		fmt.Printf("索引已存在：%d 块（重建加 --rebuild）\n", col.Count())
		return nil
	}

	docs, err := loadDocuments(cfg.RepoRoot)
	if err != nil {
		return err
	}
	chunks := splitDocuments(docs, cfg.ChunkSize, cfg.ChunkOverlap)
	fmt.Printf("加载 %d 个文件，切分 %d 块，开始向量化（并发 %d）...\n",
		len(docs), len(chunks), cfg.Concurrency)

	const batch = 64
	ctx := context.Background()
	start := time.Now()
	for i := 0; i < len(chunks); i += batch {
		end := min(i+batch, len(chunks))
		batchDocs := make([]chromem.Document, 0, end-i)
		for _, c := range chunks[i:end] {
			batchDocs = append(batchDocs, chromem.Document{
				ID:      c.ID,
				Content: c.Content,
				Metadata: map[string]string{
					"source":  c.Source,
					"chapter": c.Chapter,
					"h1":      c.H1,
					"h2":      c.H2,
					"h3":      c.H3,
				},
			})
		}
		if err := col.AddDocuments(ctx, batchDocs, cfg.Concurrency); err != nil {
			return fmt.Errorf("写入第 %d~%d 块失败: %w", i, end, err)
		}
		fmt.Printf("  写入 %d/%d，用时 %s\n", end, len(chunks), time.Since(start).Round(time.Second))
	}

	fmt.Printf("完成。集合 %s 共 %d 块，数据目录 %s\n", cfg.Collection, col.Count(), cfg.DataDir)
	return nil
}
