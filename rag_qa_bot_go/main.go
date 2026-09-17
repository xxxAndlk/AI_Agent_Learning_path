package main

import (
	"bufio"
	"context"
	"flag"
	"fmt"
	"os"
	"strings"

	"github.com/openai/openai-go"
)

const usage = `用法：go run . <命令> [参数]

  check              连通性自检（各发一次 LLM / Embedding 请求）
  ingest              只加载 + 切分，打印统计（不调用 API，验证排除规则和切分效果）
  build [--rebuild]   建索引（向量化并写入本地向量库）
  search <问题> [--k 6] [--chapter "05.RAG系统（重点）"] [--mmr]
                      只检索，不接 LLM（调检索用）
  ask <问题>          单轮问答（流式输出）
  chat                多轮对话（带追问改写）
  serve [--addr :8080]
                      Web UI
  eval [--k 6]        检索命中率评测
`

func main() {
	if len(os.Args) < 2 {
		fmt.Print(usage)
		os.Exit(1)
	}

	switch os.Args[1] {
	case "check":
		cmdCheck()

	case "ingest":
		cmdIngest()

	case "build":
		fs := flag.NewFlagSet("build", flag.ExitOnError)
		rebuild := fs.Bool("rebuild", false, "删掉旧索引重建（换 Embedding 模型后必须加）")
		fs.Parse(os.Args[2:])
		must(buildIndex(*rebuild))

	case "search":
		fs := flag.NewFlagSet("search", flag.ExitOnError)
		k := fs.Int("k", cfg.TopK, "返回条数")
		chapter := fs.String("chapter", "", "只在该章节内检索")
		mmr := fs.Bool("mmr", false, "使用 MMR 多样化检索")
		fs.Parse(os.Args[2:])
		if fs.NArg() == 0 {
			fmt.Println(`用法：go run . search "你的问题" [--k 6] [--chapter "..."] [--mmr]`)
			os.Exit(1)
		}
		cmdSearch(strings.Join(fs.Args(), " "), *k, *chapter, *mmr)

	case "ask":
		if len(os.Args) < 3 {
			fmt.Println(`用法：go run . ask "你的问题"`)
			os.Exit(1)
		}
		cmdAsk(strings.Join(os.Args[2:], " "))

	case "chat":
		cmdChat()

	case "serve":
		fs := flag.NewFlagSet("serve", flag.ExitOnError)
		addr := fs.String("addr", ":8080", "监听地址")
		fs.Parse(os.Args[2:])
		must(serve(*addr))

	case "eval":
		fs := flag.NewFlagSet("eval", flag.ExitOnError)
		k := fs.Int("k", cfg.TopK, "评估用的 Top-K")
		fs.Parse(os.Args[2:])
		cmdEval(*k)

	default:
		fmt.Print(usage)
		os.Exit(1)
	}
}

// 先验证钥匙能开门，再谈做事：很多"RAG 没效果"最后查出来是 Key 或 Base URL 配错了
func cmdCheck() {
	requireAPIKey()
	ctx := context.Background()

	client := newLLMClient()
	res, err := client.Chat.Completions.New(ctx, openai.ChatCompletionNewParams{
		Model:    cfg.LLMModel,
		Messages: []openai.ChatCompletionMessageParamUnion{openai.UserMessage("只回复两个字：收到")},
	})
	must(err)
	fmt.Printf("[OK] LLM %s 可用：%s\n", cfg.LLMModel, strings.TrimSpace(res.Choices[0].Message.Content))

	vec, err := embeddingFunc()(ctx, "测试一句话")
	must(err)
	fmt.Printf("[OK] Embedding %s 可用，向量维度：%d\n", cfg.EmbedModel, len(vec))
}

func cmdIngest() {
	docs, err := loadDocuments(cfg.RepoRoot)
	must(err)
	total := 0
	for _, d := range docs {
		total += runeLen(d.Text)
	}
	fmt.Printf("加载文件数：%d\n总字符数：%d\n", len(docs), total)

	chunks := splitDocuments(docs, cfg.ChunkSize, cfg.ChunkOverlap)
	minLen, sum, maxLen := 1<<30, 0, 0
	for _, c := range chunks {
		n := runeLen(c.Content)
		minLen = min(minLen, n)
		maxLen = max(maxLen, n)
		sum += n
	}
	fmt.Printf("切分后块数：%d\n块长度：min=%d 平均=%d max=%d\n",
		len(chunks), minLen, sum/max1(len(chunks)), maxLen)
}

func cmdSearch(question string, k int, chapter string, useMMR bool) {
	col, err := openCollection()
	must(err)
	requireIndex(col)
	requireAPIKey()

	var hits []Hit
	if useMMR {
		hits, err = mmrSearch(context.Background(), col, question, k, 20, 0.5)
		fmt.Printf("MMR 检索：%s（k=%d，fetch_k=20，lambda=0.5）\n", question, k)
	} else {
		hits, err = searchIndex(context.Background(), col, question, k, chapter)
		fmt.Printf("向量检索：%s（k=%d，chapter=%q）\n", question, k, chapter)
	}
	must(err)
	printHits(hits)
}

func cmdAsk(question string) {
	col, err := openCollection()
	must(err)
	requireIndex(col)
	requireAPIKey()

	sess := newChatSession(col)
	fmt.Printf("问：%s\n\n", question)
	_, hits, _, err := sess.Ask(context.Background(), question, func(delta string) {
		fmt.Print(delta)
	})
	fmt.Println()
	if err != nil {
		fmt.Fprintf(os.Stderr, "\n出错了：%v\n", err)
		os.Exit(1)
	}
	fmt.Println("\n召回的来源：")
	printHitsShort(hits)
}

func cmdChat() {
	col, err := openCollection()
	must(err)
	requireIndex(col)
	requireAPIKey()

	sess := newChatSession(col)
	fmt.Println("输入问题开始对话（exit / quit 退出）")
	scanner := bufio.NewScanner(os.Stdin)
	for {
		fmt.Print("\n你 > ")
		if !scanner.Scan() {
			break
		}
		question := strings.TrimSpace(scanner.Text())
		if question == "" {
			continue
		}
		if question == "exit" || question == "quit" {
			break
		}

		fmt.Print("\n机器人 > ")
		_, hits, standalone, err := sess.Ask(context.Background(), question, func(delta string) {
			fmt.Print(delta)
		})
		fmt.Println()
		if err != nil {
			fmt.Fprintf(os.Stderr, "出错了：%v\n", err)
			continue
		}
		if standalone != question {
			fmt.Printf("（追问改写为：%s）\n", standalone)
		}
		printHitsShort(hits)
	}
}

func cmdEval(k int) {
	col, err := openCollection()
	must(err)
	requireIndex(col)
	requireAPIKey()
	must(runEval(col, k))
}

// ---------- 小工具 ----------

func must(err error) {
	if err != nil {
		fmt.Fprintln(os.Stderr, "错误：", err)
		os.Exit(1)
	}
}

func requireIndex(col interface{ Count() int }) {
	if col.Count() == 0 {
		fmt.Fprintln(os.Stderr, "索引是空的，先运行：go run . build")
		os.Exit(1)
	}
}

func requireAPIKey() {
	if cfg.APIKey == "" {
		fmt.Fprintln(os.Stderr, "缺少 OPENAI_API_KEY（写进 .env 或设为环境变量）")
		os.Exit(1)
	}
}

func max1(n int) int {
	if n == 0 {
		return 1
	}
	return n
}
