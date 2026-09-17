package main

import (
	"context"
	"math"
	"strings"
	"testing"

	"github.com/philippgille/chromem-go"
)

// 假的 Embedding：字符袋 + 归一化。只用来验证链路，不验证语义质量。
func fakeEmbedding(dim int) chromem.EmbeddingFunc {
	return func(_ context.Context, text string) ([]float32, error) {
		v := make([]float32, dim)
		for _, r := range text {
			v[int(r)%dim] += 1
		}
		var norm float64
		for _, x := range v {
			norm += float64(x) * float64(x)
		}
		norm = math.Sqrt(norm)
		if norm > 0 {
			for i := range v {
				v[i] = float32(float64(v[i]) / norm)
			}
		}
		return v, nil
	}
}

func TestOfflinePlumbing(t *testing.T) {
	ctx := context.Background()
	dir := t.TempDir()

	db, err := chromem.NewPersistentDB(dir, false)
	if err != nil {
		t.Fatal(err)
	}
	col, err := db.GetOrCreateCollection("t", nil, fakeEmbedding(64))
	if err != nil {
		t.Fatal(err)
	}

	docs := []chromem.Document{
		{ID: "a#0#0", Content: "递归切分 chunk_size 与 chunk_overlap 的取值建议",
			Metadata: map[string]string{"source": "05.RAG系统（重点）/5.1_Chunk策略.md", "chapter": "05.RAG系统（重点）", "h1": "5.1 Chunk策略", "h2": "4 核心概念"}},
		{ID: "b#0#0", Content: "余弦相似度用于向量检索的打分",
			Metadata: map[string]string{"source": "05.RAG系统（重点）/5.2_Embedding模型.md", "chapter": "05.RAG系统（重点）", "h1": "5.2 Embedding模型"}},
	}
	if err := col.AddDocuments(ctx, docs, 2); err != nil {
		t.Fatal(err)
	}

	// 重开持久化库，验证落盘后能读回
	db2, err := chromem.NewPersistentDB(dir, false)
	if err != nil {
		t.Fatal(err)
	}
	col2, err := db2.GetOrCreateCollection("t", nil, fakeEmbedding(64))
	if err != nil {
		t.Fatal(err)
	}
	if col2.Count() != 2 {
		t.Fatalf("reopen count = %d, want 2", col2.Count())
	}

	// 检索 + 元数据过滤
	hits, err := searchIndex(ctx, col2, "chunk_size 怎么调", 1, "")
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(hits[0].Title, "5.1") {
		t.Fatalf("top hit should be 5.1, got %q", hits[0].Title)
	}

	// 上下文拼装：块前面必须带 [文件 › 小节]，引用才立得住
	ctxText := buildContext(hits)
	if !strings.Contains(ctxText, "[05.RAG系统（重点）/5.1_Chunk策略.md › 5.1 Chunk策略 › 4 核心概念]") {
		t.Fatalf("context header wrong: %s", firstRunes(ctxText, 200))
	}

	// 切分不变量：所有块 <= chunk_size + overlap
	text := "# T\n\n## A\n\n" + strings.Repeat("这是一句用于测试的中文。", 200)
	for i, c := range splitRecursive(text, 200, 40, defaultSeparators) {
		if runeLen(c) > 200+40 {
			t.Fatalf("chunk %d too long: %d runes", i, runeLen(c))
		}
	}
}
