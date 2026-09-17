package main

import (
	"context"
	"fmt"

	"github.com/philippgille/chromem-go"
)

// 检索命中率评测：问题 → 期望文件 → 看召回的块是否覆盖期望来源。
// 先跑这个，再回去调参数，每次只改一个变量。
var evalCases = []struct {
	Q      string
	Expect []string
}{
	{"RAG 和微调的区别是什么", []string{"05.RAG系统（重点）/5.3_RAG_Pipeline.md"}},
	{"5.1 里讲了哪几种切分策略", []string{"05.RAG系统（重点）/5.1_Chunk策略.md"}},
	{"LCEL 的管道操作符怎么组合", []string{"04.LangChain框架详解/4.2_LCEL表达式详解.md"}},
	{"Chroma 怎么做元数据过滤", []string{"08.向量数据库进阶/8.1_Chroma向量数据库.md"}},
	{"BGE-M3 的向量维度是多少", []string{"05.RAG系统（重点）/5.2_Embedding模型.md"}},
	{"重排序模型怎么用", []string{"05.RAG系统（重点）/5.6_Rerank模型.md"}},
	{"FAISS 有哪些索引类型", []string{"07.向量数据库/7.2_FAISS高级用法.md"}},
	{"12.1 项目的 requirements.txt 里有什么", []string{"12.实战项目（完整代码）/12.1_本地知识库RAG.md"}},
	{"怎么防止 Prompt 注入", []string{"06.Agent系统与智能体/6.3_LLM安全与对齐.md"}},
	{"多 Agent 之间怎么协作", []string{"06.Agent系统与智能体/6.9_Multi-Agent系统.md"}},
}

func runEval(col *chromem.Collection, k int) error {
	ctx := context.Background()
	hit := 0
	for _, c := range evalCases {
		hits, err := searchIndex(ctx, col, c.Q, k, "")
		if err != nil {
			return err
		}
		found := false
		var got []string
		seen := map[string]bool{}
		for _, h := range hits {
			if !seen[h.Source] {
				seen[h.Source] = true
				got = append(got, h.Source)
			}
			for _, e := range c.Expect {
				if h.Source == e {
					found = true
				}
			}
		}
		if found {
			hit++
			fmt.Printf("✅ k=%d %s\n", k, c.Q)
		} else {
			fmt.Printf("❌ k=%d %s\n     期望：%v\n     实际召回：%v\n", k, c.Q, c.Expect, got)
		}
	}
	fmt.Printf("\n命中率：%d/%d = %.0f%%\n", hit, len(evalCases), float64(hit)/float64(len(evalCases))*100)
	return nil
}
