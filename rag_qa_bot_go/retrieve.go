package main

import (
	"context"
	"fmt"
	"math"
	"strings"

	"github.com/philippgille/chromem-go"
)

type Hit struct {
	Source     string
	Title      string
	Similarity float32
	Content    string
}

func searchIndex(ctx context.Context, col *chromem.Collection, query string, k int, chapter string) ([]Hit, error) {
	// chromem 要求 nResults <= 集合里的文档数，否则报错；k 调大时这里兜一下
	if n := col.Count(); k > n {
		k = n
	}
	var where map[string]string
	if chapter != "" {
		where = map[string]string{"chapter": chapter} // 元数据过滤：只在这一章里找
	}
	results, err := col.Query(ctx, query, k, where, nil)
	if err != nil {
		return nil, err
	}
	hits := make([]Hit, 0, len(results))
	for _, r := range results {
		hits = append(hits, Hit{
			Source:     r.Metadata["source"],
			Title:      titleOf(r.Metadata),
			Similarity: r.Similarity,
			Content:    r.Content,
		})
	}
	return hits, nil
}

// MMR：在"相关"和"多样"之间折中，避免 Top-K 全是同一小节的重复内容
func mmrSearch(ctx context.Context, col *chromem.Collection, query string, k, fetchK int, lambda float32) ([]Hit, error) {
	qVec, err := embeddingFunc()(ctx, query)
	if err != nil {
		return nil, err
	}
	if n := col.Count(); fetchK > n {
		fetchK = n
	}
	candidates, err := col.Query(ctx, query, fetchK, nil, nil)
	if err != nil {
		return nil, err
	}

	type cand struct {
		r      chromem.Result
		v      []float32
		maxSim float32 // 与已选中内容的最大相似度
	}
	cands := make([]cand, 0, len(candidates))
	for _, r := range candidates {
		doc, err := col.GetByID(ctx, r.ID) // 取回向量，用于候选之间互相比较
		if err != nil {
			return nil, err
		}
		cands = append(cands, cand{r: r, v: doc.Embedding})
	}

	var picked []Hit
	for len(picked) < k && len(cands) > 0 {
		bestIdx, bestScore := 0, float32(math.Inf(-1))
		for i, c := range cands {
			score := lambda*cosine(qVec, c.v) - (1-lambda)*c.maxSim
			if score > bestScore {
				bestIdx, bestScore = i, score
			}
		}
		chosen := cands[bestIdx]
		picked = append(picked, Hit{
			Source:     chosen.r.Metadata["source"],
			Title:      titleOf(chosen.r.Metadata),
			Similarity: chosen.r.Similarity,
			Content:    chosen.r.Content,
		})

		cands = append(cands[:bestIdx], cands[bestIdx+1:]...)
		for i := range cands {
			if s := cosine(chosen.v, cands[i].v); s > cands[i].maxSim {
				cands[i].maxSim = s
			}
		}
	}
	return picked, nil
}

func cosine(a, b []float32) float32 {
	var dot, na, nb float64
	for i := range a {
		dot += float64(a[i]) * float64(b[i])
		na += float64(a[i]) * float64(a[i])
		nb += float64(b[i]) * float64(b[i])
	}
	if na == 0 || nb == 0 {
		return 0
	}
	return float32(dot / math.Sqrt(na*nb))
}

func printHits(hits []Hit) {
	for i, h := range hits {
		fmt.Printf("\n[%d] 相似度 %.3f | %s\n", i+1, h.Similarity, h.Source)
		if h.Title != "" {
			fmt.Printf("    小节：%s\n", h.Title)
		}
		fmt.Printf("    %s ...\n", firstRunes(strings.ReplaceAll(h.Content, "\n", " "), 120))
	}
}
