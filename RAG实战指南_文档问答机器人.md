# RAG 实战指南（Go 技术栈）：给本仓库文档做一个智能问答机器人

> 本文是一份**动手教程**：从零开始，用 **Go** 把当前仓库里 14 章 77 节的学习资料做成知识库，最终得到一个可以多轮追问、回答带出处引用、支持流式输出的问答机器人（命令行 + Web 界面）。
>
> 配套章节：`5.1 Chunk策略`、`5.2 Embedding模型`、`5.3 RAG_Pipeline`、`8.1 Chroma向量数据库`（Go 里对应嵌入式向量库 chromem-go）、`12.1 本地知识库RAG`、`14.2 AI聊天应用`（流式响应）。
>
> 本文是"最短可跑通路径"：原理遇到不懂的地方，回查对应章节。文中所有 Go 代码都经过 `go build` / `go vet` / 离线链路测试验证。

---

## 目录

- [0 开工之前](#0-开工之前)
- [1 步骤一：环境、配置与文档加载](#1-步骤一环境配置与文档加载)
- [2 步骤二：切分文本块（Chunk）](#2-步骤二切分文本块chunk)
- [3 步骤三：连通性自检与建索引](#3-步骤三连通性自检与建索引)
- [4 步骤四：只验证检索（先别接 LLM）](#4-步骤四只验证检索先别接-llm)
- [5 步骤五：接上 LLM，生成带引用的回答](#5-步骤五接上-llm生成带引用的回答)
- [6 步骤六：多轮对话（追问改写）](#6-步骤六多轮对话追问改写)
- [7 步骤七：Web UI（流式输出 + SSE）](#7-步骤七web-ui流式输出--sse)
- [8 步骤八：评测与调优](#8-步骤八评测与调优)
- [9 收尾：代码清单与学习地图](#9-收尾代码清单与学习地图)
- [附录 A 常见报错速查](#附录-a-常见报错速查)
- [附录 B 零成本本地方案（Ollama）](#附录-b-零成本本地方案ollama)
- [附录 C 参数速查表](#附录-c-参数速查表)
- [附录 D 完整 main.go 与"假 Embedding"离线测试](#附录-d-完整-maingo-与假-embedding离线测试)
- [附录 E 换生产级向量库（Milvus / Qdrant / PGVector）](#附录-e-换生产级向量库milvus--qdrant--pgvector)

---

## 0 开工之前

### 0.1 最终效果

```text
$ go run . ask "RAG 和微调的区别是什么"

问：RAG 和微调的区别是什么

RAG 不需要重新训练，知识可以动态更新，而且回答能追溯到源文档；微调则是把
知识编码进模型参数，适合任务模式固定的场景 [来源: 05.RAG系统（重点）/5.3_RAG_Pipeline.md › 5.3 RAG Pipeline › 2.3 RAG vs 微调]。
...

依据的是 5.3 RAG Pipeline 的"RAG vs 微调"小节。

召回的来源：
  [1] 05.RAG系统（重点）/5.3_RAG_Pipeline.md › 5.3 RAG Pipeline › 2.3 RAG vs 微调
  ...

$ go run . chat          # 多轮追问，带改写
$ go run . serve         # 浏览器打开 http://localhost:8080
$ go run . eval          # 检索命中率评测
```

### 0.2 技术选型（Go 栈）

| 环节 | 选择 | 说明 |
|------|------|------|
| LLM / Embedding 调用 | `github.com/openai/openai-go`（官方 SDK，v1.12.0） | OpenAI 兼容协议，换 `OPENAI_BASE_URL` 即接中转网关 / Ollama / vLLM |
| 向量库 | `github.com/philippgille/chromem-go`（v0.7.0） | 纯 Go 嵌入式向量库，落盘到本地文件，相当于 Python 侧的嵌入式 Chroma：**不用起服务** |
| 配置 | `github.com/joho/godotenv` | 读 `.env` |
| Web | 标准库 `net/http` + `html/template` + SSE | 不引第三方 Web 框架；流式输出对应 `14.2 AI聊天应用` |
| 切分 / 检索 / 评测 | 自己写（约 200 行） | Go 生态没有 LangChain 那种"全家桶"，薄封装反而更可控；确需框架可了解 `tmc/langchaingo` |

> **为什么不直接用 langchaingo？** 它是最接近 Python LangChain 的 Go 方案，但组件成熟度和文档都不如原版，RAG 部分抽象反而遮住关键细节。本教程用官方 SDK + 自写流水线：每一步都看得见、改得动。数据量上到百万级要换 Milvus/Qdrant 时，只需替换 `index.go` / `retrieve.go` 里的存取层（见附录 E）。

### 0.3 知识库范围

| 纳入 | 排除 |
|------|------|
| 01~14 章目录下全部 `.md`（77 节） | `README.md`（项目介绍，不是知识内容） |
| `大纲.md` | `修改记录_v4.1~v4.4.md`（版本流水账） |
| 根目录的教程文档（含本文） | `rag_qa_bot_go/`（本项目自己的代码与数据） |

总量：**80 个文件、约 300 万字符**（实测值见步骤一）。规模很小：一次全量 embedding 只有几美分，检索是内存暴力扫描，毫秒级。

### 0.4 整体架构

```text
┌──────────── 离线：建索引（只跑一次，改了文档再跑） ────────────┐
│  .md 文件 → 加载 → 按标题两级切分 → Embedding → chromem 落盘    │
└───────────────────────────────────────────────────────────────┘
┌──────────── 在线：问答（每次提问都走这条链） ──────────────────┐
│  提问 → 追问改写 → 向量检索 Top-K → 拼 Prompt → LLM → 带引用回答 │
└───────────────────────────────────────────────────────────────┘
```

### 0.5 目录规划

代码放在仓库根目录下新建的 `rag_qa_bot_go/`（加载器会跳过这个目录，机器人不会把自己的代码当知识库）：

```text
AI应用开发技术栈目录/
├── rag_qa_bot_go/
│   ├── .env            # API Key 等配置（不提交到 git）
│   ├── go.mod / go.sum
│   ├── config.go       # 配置 + LLM 客户端
│   ├── ingest.go       # 加载 + 切分
│   ├── index.go        # 向量化 + 建索引
│   ├── retrieve.go     # 检索（含 MMR）
│   ├── rag.go          # Prompt / 生成 / 多轮会话
│   ├── eval.go         # 检索命中率评测
│   ├── web.go          # Web UI（SSE 流式）
│   ├── main.go         # 命令入口
│   └── data/           # 向量库落盘目录（不提交到 git）
├── 01.Python快速入门（Go开发者版）/
└── ...
```

顺手把这两行加进仓库根目录的 `.gitignore`（**别把 API Key 提交上去**）：

```gitignore
rag_qa_bot_go/.env
rag_qa_bot_go/data/
```

### 0.6 时间预算

| 阶段 | 耗时 |
|------|------|
| 环境 + 加载 + 切分 | 20 分钟 |
| 建索引（等 API 跑完） | 3~8 分钟 |
| 检索调优 + 问答 + Web UI | 40 分钟 |
| 评测 | 15 分钟 |

---

## 1 步骤一：环境、配置与文档加载

### 1.1 建项目

需要 **Go 1.21+**（代码用到了内置 `min`；本文在 Go 1.25.4 上验证）。国内建议先设模块代理：

```bash
cd "D:\data\demo\py_AI_doc\AI应用开发技术栈目录"
mkdir rag_qa_bot_go && cd rag_qa_bot_go

go mod init ragqabot
go env -w GOPROXY=https://goproxy.cn,direct     # 国外网络可省略

go get github.com/openai/openai-go@v1.12.0
go get github.com/philippgille/chromem-go@v0.7.0
go get github.com/joho/godotenv@v1.5.1
```

`go.mod` 最终长这样：

```text
module ragqabot

go 1.25.4

require (
	github.com/joho/godotenv v1.5.1
	github.com/openai/openai-go v1.12.0
	github.com/philippgille/chromem-go v0.7.0
)

require (
	github.com/tidwall/gjson v1.14.4 // indirect
	github.com/tidwall/match v1.1.1 // indirect
	github.com/tidwall/pretty v1.2.1 // indirect
	github.com/tidwall/sjson v1.2.5 // indirect
)
```

### 1.2 配置 .env

新建 `rag_qa_bot_go/.env`：

```env
OPENAI_API_KEY=sk-你的key
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-5.4-mini
EMBEDDING_MODEL=text-embedding-3-small
```

国内中转网关或本地 Ollama，只改 `OPENAI_BASE_URL` 和模型名（见附录 B）。**`OPENAI_BASE_URL` 要带 `/v1`，结尾不要斜杠。**

### 1.3 config.go：配置集中一处

```go
// rag_qa_bot_go/config.go
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
```

### 1.4 ingest.go：加载部分

加载就是把每个 `.md` 读成带**元数据**（相对路径、所属章节目录）的 `Doc`。元数据现在不起眼，到"回答带引用"和"按章节过滤检索"时是刚需。对应 `5.3 RAG Pipeline` 的"文档加载"环节。

```go
// rag_qa_bot_go/ingest.go（第一部分：加载）
package main

import (
	"io/fs"
	"os"
	"path/filepath"
	"strings"
)

type Doc struct {
	Source  string // 仓库内相对路径，统一用 /（Windows 上也一样）
	Chapter string
	Text    string
}

type Chunk struct {
	ID      string // 文件路径 # 小节序号 # 块序号，确定性 ID 让重复写入变成覆盖
	Source  string
	Chapter string
	H1      string
	H2      string
	H3      string
	Content string
}

// 加载知识库时排除的文件 / 目录
var (
	excludeFiles    = map[string]bool{"README.md": true}
	excludePrefixes = []string{"修改记录_"}
	excludeDirs     = map[string]bool{
		".git": true, ".venv": true, "venv": true,
		"__pycache__": true, "node_modules": true, "rag_qa_bot": true,
	}
)

func loadDocuments(root string) ([]Doc, error) {
	var docs []Doc
	err := filepath.WalkDir(root, func(path string, d fs.DirEntry, err error) error {
		if err != nil {
			return err
		}
		name := d.Name()
		if d.IsDir() {
			if path == root {
				return nil
			}
			// 跳过本项目自身、隐藏目录（.git 等）、依赖目录
			if filepath.Clean(path) == filepath.Clean(cfg.ProjectDir) {
				return filepath.SkipDir
			}
			if strings.HasPrefix(name, ".") || excludeDirs[name] {
				return filepath.SkipDir
			}
			return nil
		}
		if !strings.HasSuffix(name, ".md") || excludeFiles[name] {
			return nil
		}
		for _, p := range excludePrefixes {
			if strings.HasPrefix(name, p) {
				return nil
			}
		}

		raw, err := os.ReadFile(path)
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		rel = filepath.ToSlash(rel)
		chapter := "根目录"
		if i := strings.Index(rel, "/"); i > 0 {
			chapter = rel[:i]
		}
		// 本仓库文档是 CRLF；统一成 LF，避免 \r 混进 chunk 和向量里
		text := strings.ReplaceAll(string(raw), "\r\n", "\n")
		docs = append(docs, Doc{Source: rel, Chapter: chapter, Text: text})
		return nil
	})
	return docs, err
}
```

> 后面步骤往这个文件里追加代码时，记得同步补 import：切分部分会用到 `fmt` 和 `unicode/utf8`。（Go 对"导入了没用"和"用了没导入"都是编译错误，这一步开始就要养成习惯。）

### 1.5 main.go：命令入口（先只接 ingest）

```go
// rag_qa_bot_go/main.go
package main

import (
	"fmt"
	"os"
)

const usage = `用法：go run . <命令> [参数]

  ingest              只加载 + 切分，打印统计（不调用 API，验证排除规则和切分效果）
`

func main() {
	if len(os.Args) < 2 {
		fmt.Print(usage)
		os.Exit(1)
	}

	switch os.Args[1] {
	case "ingest":
		cmdIngest()
	default:
		fmt.Print(usage)
		os.Exit(1)
	}
}

func cmdIngest() {
	docs, err := loadDocuments(cfg.RepoRoot)
	must(err)
	total := 0
	for _, d := range docs {
		total += runeLen(d.Text)
	}
	fmt.Printf("加载文件数：%d\n总字符数：%d\n", len(docs), total)
}

func must(err error) {
	if err != nil {
		fmt.Fprintln(os.Stderr, "错误：", err)
		os.Exit(1)
	}
}
```

`runeLen` 放在 ingest.go 末尾（步骤二之后会一起补上）：

```go
func runeLen(s string) int { return utf8.RuneCountInString(s) }
```

### 1.6 跑起来

```bash
go run . ingest
# 加载文件数：80
# 总字符数：2991041
```

### 1.7 检查点

- 文件数 **80**（77 节 + `大纲.md` + 两份教程文档）。明显偏少 → 排除规则写错。
- 抽查几条，`source` 里没有 `README.md`、没有 `修改记录_`、没有 `rag_qa_bot_go/`。

### 1.8 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| Windows 终端中文输出乱码 | 控制台代码页是 GBK | `chcp 65001` 切 UTF-8，或换 Windows Terminal / VS Code 终端 |
| `go get` 卡住 / 超时 | 模块代理不通 | `go env -w GOPROXY=https://goproxy.cn,direct` |
| `source` 里出现 `\` 反斜杠 | 直接拼接 `path` 的结果 | 用 `filepath.Rel` + `filepath.ToSlash`（本文已处理） |
| 加载内容里混入 `\r` | 仓库文档是 CRLF（v4.4 校订统一过） | 读入时 `strings.ReplaceAll(text, "\r\n", "\n")`（本文已处理，实测能差出 11 万个字符） |

---

## 2 步骤二：切分文本块（Chunk）

### 2.1 做什么

把每个大文档切成 **500~1000 字符**的小块。这是 RAG 里**最值得花时间调**的一步：切得好，检索基本就对了。对应 `5.1 Chunk策略`，用它的推荐组合——**结构感知切分 + 递归字符切分**，两级：

1. **按 Markdown 标题切**（`# / ## / ###`）：每个小节独立成段，标题写进元数据，检索结果天然带"我是谁"。
2. **超长小节再递归切**：按优先级 `\n## → \n### → \n\n → \n → 。 → ； → ， → 空格 → 硬切`，从最"像边界"的地方切起。

Go 里没有现成组件，自己写约 150 行——比拉一个框架上来更值，因为**切分是你要反复调的地方，代码必须握在自己手里**。

### 2.2 第一级：按标题切（带代码块保护）

```go
// rag_qa_bot_go/ingest.go（续，追加到文件末尾）

type section struct {
	H1, H2, H3 string
	Content    string
}

func splitByHeaders(text string) []section {
	var sections []section
	var cur section
	var buf strings.Builder

	flush := func() {
		if strings.TrimSpace(buf.String()) != "" {
			cur.Content = strings.TrimSpace(buf.String())
			sections = append(sections, cur)
		}
		buf.Reset()
	}

	inFence := false
	for _, line := range strings.Split(text, "\n") {
		t := strings.TrimSpace(line)
		if strings.HasPrefix(t, "```") {
			inFence = !inFence // 代码块里的 # 不是标题
		}
		if !inFence {
			switch {
			case strings.HasPrefix(t, "# "):
				flush()
				cur.H1, cur.H2, cur.H3 = strings.TrimSpace(t[2:]), "", ""
			case strings.HasPrefix(t, "## "):
				flush()
				cur.H2, cur.H3 = strings.TrimSpace(t[3:]), ""
			case strings.HasPrefix(t, "### "):
				flush()
				cur.H3 = strings.TrimSpace(t[4:])
			}
		}
		buf.WriteString(line)
		buf.WriteByte('\n')
	}
	flush()
	return sections
}
```

**代码块保护是必需的**：本仓库有 1100+ 个代码块，Python 注释 `# 注释` 和代码里的 `##` 会被误判成标题。`inFence` 开关解决这个问题。

### 2.3 第二级：递归字符切分（按 rune 计数）

```go
// rag_qa_bot_go/ingest.go（续）

var defaultSeparators = []string{"\n## ", "\n### ", "\n\n", "\n", "。", "；", "，", " ", ""}

// 从最长分隔符开始尝试；片段仍然超长就换下一级分隔符，都不行就硬切。
func splitRecursive(text string, size, overlap int, seps []string) []string {
	if runeLen(text) <= size {
		if strings.TrimSpace(text) == "" {
			return nil
		}
		return []string{text}
	}
	if len(seps) == 0 || seps[0] == "" {
		return hardSplit(text, size, overlap)
	}

	var out []string
	var cur strings.Builder
	flush := func(seed bool) {
		s := strings.TrimSpace(cur.String())
		if s != "" {
			out = append(out, s)
		}
		cur.Reset()
		if seed && s != "" {
			cur.WriteString(tailRunes(s, overlap)) // 相邻块之间保留重叠
		}
	}

	for _, part := range splitKeepingSep(text, seps[0]) {
		if runeLen(part) > size {
			flush(true)
			sub := splitRecursive(part, size, overlap, seps[1:])
			out = append(out, sub...)
			cur.Reset()
			if len(sub) > 0 {
				cur.WriteString(tailRunes(sub[len(sub)-1], overlap))
			}
			continue
		}
		// cur 里只剩重叠尾巴（长度 <= overlap）时不能再触发 flush，否则会死循环
		if runeLen(cur.String()) > overlap && runeLen(cur.String())+runeLen(part) > size {
			flush(true)
		}
		cur.WriteString(part)
	}
	flush(false)
	return out
}

// 按分隔符切开，分隔符留在前一片段的末尾（尽量不破坏句子）
func splitKeepingSep(text, sep string) []string {
	var parts []string
	for len(text) > 0 {
		i := strings.Index(text, sep)
		if i < 0 {
			parts = append(parts, text)
			break
		}
		end := i + len(sep)
		parts = append(parts, text[:end])
		text = text[end:]
	}
	return parts
}

// 到最后一个分隔符也切不开时，按 rune 硬切
func hardSplit(text string, size, overlap int) []string {
	r := []rune(text)
	step := size - overlap
	if step <= 0 {
		step = size
	}
	var out []string
	for start := 0; start < len(r); start += step {
		end := min(start+size, len(r))
		out = append(out, string(r[start:end]))
		if end == len(r) {
			break
		}
	}
	return out
}
```

**为什么全程按 rune 计数而不是 `len(s)`？** 中文字符 UTF-8 编码占 3 字节，`len()` 会算成 3 倍长度，切出来的块大小完全失控。Go 里凡是处理中文长度，一律 `utf8.RuneCountInString`。

### 2.4 串起来：切分入口 + 小工具

```go
// rag_qa_bot_go/ingest.go（续）

func splitDocuments(docs []Doc, chunkSize, overlap int) []Chunk {
	var chunks []Chunk
	for _, doc := range docs {
		for si, sec := range splitByHeaders(doc.Text) {
			for ci, piece := range splitRecursive(sec.Content, chunkSize, overlap, defaultSeparators) {
				if runeLen(strings.TrimSpace(piece)) < 40 {
					continue // 丢掉过短的碎片（空小节、孤立的标题行等）
				}
				chunks = append(chunks, Chunk{
					ID:      fmt.Sprintf("%s#%d#%d", doc.Source, si, ci),
					Source:  doc.Source,
					Chapter: doc.Chapter,
					H1:      sec.H1,
					H2:      sec.H2,
					H3:      sec.H3,
					Content: strings.TrimSpace(piece),
				})
			}
		}
	}
	return chunks
}

// ---------- 小工具 ----------

func runeLen(s string) int { return utf8.RuneCountInString(s) }

func tailRunes(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[len(r)-n:])
}

func firstRunes(s string, n int) string {
	r := []rune(s)
	if len(r) <= n {
		return s
	}
	return string(r[:n])
}

// 把 h1/h2/h3 拼成 "5.1 Chunk策略 › 4 核心概念" 这样的引用路径
func titleOf(meta map[string]string) string {
	var parts []string
	for _, k := range []string{"h1", "h2", "h3"} {
		if v := meta[k]; v != "" {
			parts = append(parts, v)
		}
	}
	return strings.Join(parts, " › ")
}
```

把 `main.go` 里的 `cmdIngest` 换成带块统计的版本：

```go
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

func max1(n int) int {
	if n == 0 {
		return 1
	}
	return n
}
```

### 2.5 跑起来（实测输出）

```bash
go run . ingest
# 加载文件数：80
# 总字符数：2991041
# 切分后块数：8328
# 块长度：min=40 平均=430 max=917
```

### 2.6 检查点

- **块数**在 6000~10000 之间算正常（约 300 万字符 / 平均 430 字符）。
- **`max` 略微超过 `chunk_size`（800）是正常的**：相邻块之间保留了 120 字符重叠尾巴，所以最长约 `800+120`。不是 bug。
- 抽查任意 3 个块，看内容是不是完整句子和小节，而不是半截代码。

### 2.7 参数怎么调

| 参数 | 调大 | 调小 |
|------|------|------|
| `CHUNK_SIZE` | 上下文更完整，检索精度下降、更贵 | 检索更准，容易答不全 |
| `CHUNK_OVERLAP` | 边界信息不易丢，块数变多 | 调到 0 会切断跨块论述 |

经验值：**中文技术文档，800 / 120 先跑起来**，步骤八的评测会告诉你到底要不要改。

### 2.8 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 切成几千个碎片 | 按 `len()` 而不是 rune 计数 | 一律 `utf8.RuneCountInString` |
| 块里出现半个代码块 | 代码块比 `chunk_size` 还长 | `CHUNK_SIZE` 调到 1200+，或在切分前剥掉代码块 |
| 切片越界 panic | 直接对含中文的 string 做 `s[:n]` | 先转 `[]rune` 再切（本文的 `hardSplit` 就是这么做的） |

---

## 3 步骤三：连通性自检与建索引

### 3.1 做什么

把每个块用 Embedding 模型转成 1536 维向量，连同原文、元数据一起存进 chromem-go 并落盘到 `rag_qa_bot_go/data/`。**只跑一次**，改了文档再 `--rebuild`。

对应 `5.2 Embedding模型` + `8.1 Chroma向量数据库`。

### 3.2 先自检，再花钱

很多"RAG 没效果"最后查出来是 Key 或 Base URL 配错了。先各发一次请求验证：

在 `main.go` 的 switch 里加 `case "check": cmdCheck()`，并补上函数与两个防护：

```go
// 需要 import "context"、openai "github.com/openai/openai-go"、以及 rag.go 里的 newLLMClient（config.go 已有）
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
```

```bash
go run . check
# [OK] LLM gpt-5.4-mini 可用：收到
# [OK] Embedding text-embedding-3-small 可用，向量维度：1536
```

### 3.3 index.go：向量库读写

```go
// rag_qa_bot_go/index.go
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
```

在 `main.go` 的 switch 里加：

```text
case "build":
	fs := flag.NewFlagSet("build", flag.ExitOnError)
	rebuild := fs.Bool("rebuild", false, "删掉旧索引重建（换 Embedding 模型后必须加）")
	fs.Parse(os.Args[2:])
	must(buildIndex(*rebuild))
```

（`case "check":` 那行也一并加上；`flag` 记得进 import。）

### 3.4 三个关键设计

1. **选 chromem-go 而不是 Milvus**：纯 Go、无需服务、自带落盘，对应 `8.3 向量数据库选型指南` 里"快速原型"那一档。数据量到百万级再按附录 E 换。
2. **相似度用余弦**：chromem 默认对向量做归一化后按余弦相似度算分，OpenAI 系 embedding 正是这么用的，**不用也不该改成 L2**。
3. **确定性 ID**：`文件路径#小节序号#块序号`。同样的内容重复写入是覆盖而不是新增——想增量更新时只 add 变化的文件即可。

### 3.5 跑起来

```bash
go run . build
# 加载 80 个文件，切分 8328 块，开始向量化（并发 8）...
#   写入 64/8328，用时 2s
#   ...
# 完成。集合 ai_stack_docs 共 8328 块，数据目录 ...\data\chromem_db
```

8000 多块、`text-embedding-3-small`，**成本大约几美分**，全量 3~8 分钟，别怕重跑。

### 3.6 检查点

```bash
go run . build          # 第二次运行应直接提示"索引已存在：8328 块"
ls data/chromem_db      # 应能看到 .gob 文件（chromem 的落盘格式）
```

### 3.7 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 换 Embedding 模型后检索全乱 | 维度/向量空间变了，旧索引没意义 | `go run . build --rebuild`，**换模型必须重建** |
| 写入报 429 / 超时 | 并发太高或网络抖动 | `EMBED_CONCURRENCY=4` 重跑；已写入的块不会重复计费 |
| 建索引中断了 | — | 直接重跑；确定性 ID 保证重复写入是覆盖，不会产生重复数据 |
| 想换向量库 | 接口不同 | 只需要改 `index.go` / `retrieve.go`（附录 E） |

---

## 4 步骤四：只验证检索（先别接 LLM）

### 4.1 为什么先做这一步

**RAG 的问题 90% 出在检索，不在生成。** 检索错了，模型再强也只能在错误上下文里编。所以先单测检索：不接 LLM，直接看"我这个问题，召回的都是什么块、相似度多少、来自哪个文件"。

这一步的产出是一份**自测问题清单**，步骤八的评测直接复用。

### 4.2 retrieve.go：检索 + MMR

```go
// rag_qa_bot_go/retrieve.go
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
```

在 `main.go` 里加 `case "search"` 和 `cmdSearch`：

```go
// switch 里：
// case "search":
// 	fs := flag.NewFlagSet("search", flag.ExitOnError)
// 	k := fs.Int("k", cfg.TopK, "返回条数")
// 	chapter := fs.String("chapter", "", "只在该章节内检索")
// 	mmr := fs.Bool("mmr", false, "使用 MMR 多样化检索")
// 	fs.Parse(os.Args[2:])
// 	cmdSearch(strings.Join(fs.Args(), " "), *k, *chapter, *mmr)

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
```

### 4.3 跑一组"标准问题"

用**已知答案**的问题验证召回，标准是"召回的块里确实包含答案所在的小节"：

```bash
go run . search "RAG 和微调的区别是什么"
go run . search "5.1 里讲了哪几种切分策略"
go run . search "LCEL 的管道操作符怎么用"
go run . search "Chroma 怎么做元数据过滤"
go run . search "BGE-M3 的向量维度是多少"
go run . search "12.1 那个项目用什么做 UI"

# 元数据过滤：只在这一章里找
go run . search "重排序怎么做" --chapter "05.RAG系统（重点）"

# MMR：结果更分散，不容易全挤在同一小节
go run . search "Agent 的记忆系统怎么设计" --mmr
```

### 4.4 检查点

| 症状 | 判断 | 处理 |
|------|------|------|
| Top-1 就是答案所在小节 | 检索健康，进入步骤五 | — |
| 答案在第 3~6 名 | 召回够用但不精 | 步骤八加 Rerank，或把 `k` 调到 8 |
| 相似度都低于 0.3 且不相关 | 召回失败 | 先换问题的表述 → 再调 `CHUNK_SIZE` 重建 → 换中文更强的 embedding（`bge-m3`） |
| 前 3 名全来自同一文件、内容重复 | MMR 该上场了 | 加 `--mmr` |
| 问代码怎么写，召回全是概念解释 | 索引被切的代码块干扰 | 重建时把 `CHUNK_SIZE` 调大，或剥掉代码块 |

### 4.5 关于相似度阈值

别用"相似度低于 0.75 就拒答"这种硬阈值——**余弦相似度的绝对值在不同模型间不可比**：同一句话在 `text-embedding-3-small` 上可能是 0.45，换个模型就是 0.72。更稳的做法是让 LLM 判断"上下文是否足够回答"（写进 Prompt，见 5.3）。

### 4.6 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| `nResults must be <= the number of documents` | chromem 的硬性检查，`k` 大于集合大小 | 本文 `searchIndex` 已自动钳制；自己写查询时注意 |
| `--chapter` 过滤后结果为空 | `where` 是**精确匹配**，章节名要一字不差 | 用 `go run . search "..." ` 不带过滤先看召回里的 `chapter` 值长什么样 |

---

## 5 步骤五：接上 LLM，生成带引用的回答

### 5.1 做什么

拿召回的 Top-K 拼成上下文，加上"只依据上下文回答 + 标注出处 + 不知道就说不知道"的 Prompt，输出答案和来源。对应 `5.3 RAG Pipeline` 的生成环节。

### 5.2 rag.go：Prompt + 生成

```go
// rag_qa_bot_go/rag.go（第一部分：Prompt 与生成）
package main

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/openai/openai-go"
)

const systemPrompt = `你是「AI 应用开发技术栈」学习资料的答疑助手。

规则：
1. 只依据 <上下文> 回答。上下文里没有的信息，直接说「资料里没有提到」，不要凭常识补充，更不要编造。
2. 用中文回答，尽量具体：参数、结论、代码要点都从上下文里取，别泛泛而谈。
3. 每个关键结论后用 [来源: 文件路径 › 小节标题] 标注出处，最多标 3 处。
4. 如果多个文档结论有冲突，指出冲突并分别标注来源。
5. 回答末尾用一句话说明「依据的是哪几个小节」，方便读者回查。`

type Msg struct {
	Role    string // "user" 或 "assistant"
	Content string
}

func buildContext(hits []Hit) string {
	blocks := make([]string, 0, len(hits))
	for _, h := range hits {
		head := h.Source
		if h.Title != "" {
			head = h.Source + " › " + h.Title
		}
		blocks = append(blocks, "["+head+"]\n"+h.Content)
	}
	return strings.Join(blocks, "\n\n---\n\n")
}

func chatParams(history []Msg, contextText, question string) openai.ChatCompletionNewParams {
	msgs := []openai.ChatCompletionMessageParamUnion{openai.SystemMessage(systemPrompt)}
	for _, m := range history {
		if m.Role == "user" {
			msgs = append(msgs, openai.UserMessage(m.Content))
		} else {
			msgs = append(msgs, openai.AssistantMessage(m.Content))
		}
	}
	msgs = append(msgs, openai.UserMessage(
		"<上下文>\n"+contextText+"\n</上下文>\n\n问题："+question,
	))
	return openai.ChatCompletionNewParams{
		Model:       cfg.LLMModel,
		Temperature: openai.Float(0),
		Messages:    msgs,
	}
}

func generate(ctx context.Context, client openai.Client, history []Msg, contextText, question string) (string, error) {
	res, err := client.Chat.Completions.New(ctx, chatParams(history, contextText, question))
	if err != nil {
		return "", err
	}
	if len(res.Choices) == 0 {
		return "", errors.New("模型没有返回任何内容")
	}
	return res.Choices[0].Message.Content, nil
}

// onDelta 每收到一小段增量文本就回调一次，CLI 直接打印，Web 端走 SSE 推给浏览器
func generateStream(ctx context.Context, client openai.Client, history []Msg, contextText, question string, onDelta func(string)) (string, error) {
	stream := client.Chat.Completions.NewStreaming(ctx, chatParams(history, contextText, question))
	defer stream.Close()

	var sb strings.Builder
	for stream.Next() {
		chunk := stream.Current()
		if len(chunk.Choices) == 0 {
			continue
		}
		if d := chunk.Choices[0].Delta.Content; d != "" {
			sb.WriteString(d)
			if onDelta != nil {
				onDelta(d)
			}
		}
	}
	if err := stream.Err(); err != nil {
		return sb.String(), err
	}
	return sb.String(), nil
}

func printHitsShort(hits []Hit) {
	for i, h := range hits {
		line := fmt.Sprintf("  [%d] %s", i+1, h.Source)
		if h.Title != "" {
			line += " › " + h.Title
		}
		fmt.Println(line)
	}
}
```

> 说明：`generate`（非流式）保留着，方便脚本里一次性拿完整答案；`cmdAsk` 和 Web 端用的是 `generateStream`。追加步骤六的代码时会用到 `github.com/philippgille/chromem-go`（`ChatSession` 持有 `*chromem.Collection`），记得补 import。

在 `main.go` 里加 `case "ask"` 和 `cmdAsk`：

```go
// switch 里：
// case "ask":
// 	cmdAsk(strings.Join(os.Args[2:], " "))

func cmdAsk(question string) {
	col, err := openCollection()
	must(err)
	requireIndex(col)
	requireAPIKey()

	client := newLLMClient()
	hits, err := searchIndex(context.Background(), col, question, cfg.TopK, "")
	must(err)

	fmt.Printf("问：%s\n\n", question)
	if _, err := generateStream(context.Background(), client, nil, buildContext(hits), question,
		func(delta string) { fmt.Print(delta) }); err != nil {
		fmt.Fprintf(os.Stderr, "\n出错了：%v\n", err)
		os.Exit(1)
	}
	fmt.Println("\n\n召回的来源：")
	printHitsShort(hits)
}
```

> 说明：这里的 `cmdAsk` 是"步骤五"的过渡版本（直接检索 + 生成）。步骤六会把它并入 `ChatSession`，得到带历史的完整版。

### 5.3 上下文怎么拼：把元数据变成引用

关键在于**每个块前面带上 `文件 › 小节`**，模型才知道引用什么：

```text
[05.RAG系统（重点）/5.1_Chunk策略.md › 5.1 Chunk策略 › 4 核心概念]
（正文……）

---

[04.LangChain框架详解/4.2_LCEL表达式详解.md › 4.2 LCEL表达式详解 › 3 工作原理]
（正文……）
```

### 5.4 跑起来

```bash
go run . ask "RAG 和微调的区别是什么"
```

期望：答案流式打出来，每个结论后带 `[来源: 05.RAG系统（重点）/5.3_RAG_Pipeline.md › ...]`，最后列出召回来源。

### 5.5 检查点

| 测什么 | 期望 |
|--------|------|
| 常规问题（`"5.1 讲了哪几种切分策略"`） | 答案完整，引用小节和 `search` 的召回对得上 |
| 知识库外的问题（`"今天天气怎么样"`） | 明确说"资料里没有提到"，**不硬编** |
| 边界问题（`"12.1 项目的 requirements.txt 里有什么"`） | 能答出 `langchain`、`faiss-cpu`、`chromadb` 等 |

第三行如果答不出，多半是代码块被切散了——回步骤二调 `CHUNK_SIZE` 重建。

### 5.6 内置的三个抗幻觉设计

1. `Temperature: openai.Float(0)`：降低随机性。
2. Prompt 里明确定义"不知道"的出口（规则 1）——不给出路，模型就会编。
3. 强制标注来源：**引用是幻觉的照妖镜**，答得再流畅，来源对不上就是没用。

---

## 6 步骤六：多轮对话（追问改写）

### 6.1 做什么

用户追问"那递归切分呢，重叠多少合适？"——这句话单独拿去检索，"那""它"指代不清，向量检索会跑偏。标准解法是**查询改写（Condense）**：让 LLM 结合历史把追问改写成独立问题，再拿改写后的问题检索。对应 `5.4 RAG高级主题` 的查询重写。

```text
原始追问：  "那它的重叠参数呢？"
改写后：    "5.1 Chunk策略 中递归字符切分的 chunk_overlap 参数应该设置多少？"
```

### 6.2 rag.go：会话（追加）

```go
// rag_qa_bot_go/rag.go（续，追加到文件末尾）

const condensePrompt = `根据对话历史，把用户的最新问题改写成一个不依赖上文、可独立检索的完整问题。
只输出改写后的问题，不要解释。若最新问题本身已完整，原样返回，不要画蛇添足。`

// 追问改写：没有历史时原样返回，省一次 API 调用
func rewriteQuery(ctx context.Context, client openai.Client, history []Msg, question string) (string, error) {
	if len(history) == 0 {
		return question, nil
	}
	msgs := []openai.ChatCompletionMessageParamUnion{openai.SystemMessage(condensePrompt)}
	for _, m := range history {
		if m.Role == "user" {
			msgs = append(msgs, openai.UserMessage(m.Content))
		} else {
			msgs = append(msgs, openai.AssistantMessage(m.Content))
		}
	}
	msgs = append(msgs, openai.UserMessage(question))

	res, err := client.Chat.Completions.New(ctx, openai.ChatCompletionNewParams{
		Model:       cfg.LLMModel,
		Temperature: openai.Float(0),
		Messages:    msgs,
	})
	if err != nil {
		return question, err // 改写失败不致命，退回原问题
	}
	rewritten := strings.TrimSpace(res.Choices[0].Message.Content)
	if rewritten == "" {
		return question, nil
	}
	return rewritten, nil
}

// ---------- 带历史的多轮会话 ----------

const maxHistoryMessages = 6 // 只带最近 3 轮进 Prompt，控制 token

type ChatSession struct {
	client  openai.Client
	col     *chromem.Collection
	history []Msg
}

func newChatSession(col *chromem.Collection) *ChatSession {
	return &ChatSession{client: newLLMClient(), col: col}
}

func (s *ChatSession) Ask(ctx context.Context, question string, onDelta func(string)) (answer string, hits []Hit, standalone string, err error) {
	standalone, err = rewriteQuery(ctx, s.client, trimHistory(s.history), question)
	if err != nil {
		return "", nil, question, err
	}

	hits, err = searchIndex(ctx, s.col, standalone, cfg.TopK, "")
	if err != nil {
		return "", nil, standalone, err
	}

	answer, err = generateStream(ctx, s.client, trimHistory(s.history), buildContext(hits), question, onDelta)
	if err != nil {
		return answer, hits, standalone, err
	}

	s.history = append(s.history,
		Msg{Role: "user", Content: question},
		Msg{Role: "assistant", Content: answer},
	)
	return answer, hits, standalone, nil
}

func trimHistory(h []Msg) []Msg {
	if len(h) <= maxHistoryMessages {
		return h
	}
	return h[len(h)-maxHistoryMessages:]
}
```

注意 `Ask` 的两个细节：**检索用改写后的问题（`standalone`），生成时把原问题交给模型**；历史只保留最近 3 轮，防止越聊越飘。

### 6.3 main.go：加 `chat` 命令

```go
// switch 里：
// case "chat":
// 	cmdChat()

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
```

（`bufio` 记得进 import。）另外把 `cmdAsk` 也换成走会话的版本，这样单轮问答也能复用同一套逻辑：

```go
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
```

### 6.4 跑一个多轮测试

```bash
go run . chat
```

```text
你 > 5.1 讲了哪几种切分策略？
机器人 > ...（4 类：固定 / 递归 / 语义 / 结构化）

（追问改写为：5.1 Chunk策略 中递归字符切分的 chunk_size 和 chunk_overlap 应该怎么设置？）
你 > 那它们的参数怎么调？
机器人 > ...
```

### 6.5 检查点

- 第二轮的 `（追问改写为：...）` 里，主语被补全、代词被替换成具体名词。
- 改写后的检索结果**明显比不改写好**——这是判断改写有没有生效的唯一标准。若改写后召回更差，说明改写 Prompt 太爱发挥了，"原样返回，不要画蛇添足"那句要保留。

### 6.6 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 多轮之后越答越飘 | 历史太长，早期无关内容干扰 | 调小 `maxHistoryMessages` |
| 第一轮正常，追问全崩 | 没做改写 | 检查 `Ask` 里检索用的是 `standalone` 而不是 `question` |
| 上下文超长报错 | 历史 + 召回块太多 | 减小 `TOP_K` 或历史轮数 |

---

## 7 步骤七：Web UI（流式输出 + SSE）

### 7.1 做什么

套一个 Web 界面：连续对话、**打字机式流式输出**、点开看引用。对应 `14.2 AI聊天应用` 的流式响应，只是把 Python 的 WebSocket 换成更简单的 SSE（服务端推送，单向足够）。

### 7.2 web.go

```go
// rag_qa_bot_go/web.go
package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"log"
	"net/http"
	"sync"

	"github.com/philippgille/chromem-go"
)

const pageHTML = `<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>AI 技术栈答疑机器人</title>
<style>
 body{font-family:system-ui,"Microsoft YaHei",sans-serif;max-width:820px;margin:0 auto;padding:16px}
 #log{display:flex;flex-direction:column;gap:12px;margin-bottom:16px}
 .u{align-self:flex-end;background:#dbeafe;padding:8px 12px;border-radius:12px;max-width:80%;white-space:pre-wrap}
 .a{background:#f3f4f6;padding:8px 12px;border-radius:12px;max-width:80%;white-space:pre-wrap}
 .src{font-size:12px;color:#555;margin-top:8px;border-top:1px solid #ddd;padding-top:6px}
 form{display:flex;gap:8px;position:sticky;bottom:0;background:#fff;padding:8px 0}
 input{flex:1;padding:10px;font-size:15px}
 button{padding:10px 18px}
</style>
</head>
<body>
<h3>AI 应用开发技术栈 · 文档答疑机器人</h3>
<div id="log"></div>
<form id="f"><input id="q" placeholder="问点什么，比如：5.1 讲了哪几种切分策略？" autocomplete="off"><button>发送</button></form>
<script>
const sid = Math.random().toString(36).slice(2);
const log = document.getElementById('log');
const f = document.getElementById('f'), input = document.getElementById('q');
function bubble(cls){const d=document.createElement('div');d.className=cls;log.appendChild(d);return d;}
f.addEventListener('submit', async (e) => {
  e.preventDefault();
  const question = input.value.trim();
  if (!question) return;
  input.value = '';
  bubble('u').textContent = question;
  const answerEl = bubble('a');
  answerEl.textContent = '检索并生成中…';
  const res = await fetch('/api/ask', {method:'POST', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({session_id: sid, question})});
  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = '', first = true;
  while (true) {
    const {value, done} = await reader.read();
    if (done) break;
    buf += decoder.decode(value, {stream:true});
    const events = buf.split('\n\n');
    buf = events.pop();
    for (const ev of events) {
      if (!ev.startsWith('data: ')) continue;
      const msg = JSON.parse(ev.slice(6));
      if (msg.type === 'delta') {
        if (first) { answerEl.textContent = ''; first = false; }
        answerEl.textContent += msg.text;
      } else if (msg.type === 'sources') {
        const div = document.createElement('div');
        div.className = 'src';
        div.textContent = '引用来源：' + msg.sources.map((s,i)=>'['+(i+1)+'] '+s).join('   ');
        answerEl.appendChild(div);
      } else if (msg.type === 'error') {
        answerEl.textContent = '出错了：' + msg.message;
      }
    }
  }
});
</script>
</body>
</html>`

var pageTmpl = template.Must(template.New("page").Parse(pageHTML))

type server struct {
	col      *chromem.Collection
	mu       sync.Mutex
	sessions map[string]*ChatSession
}

func (s *server) sessionFor(id string) *ChatSession {
	s.mu.Lock()
	defer s.mu.Unlock()
	sess, ok := s.sessions[id]
	if !ok {
		sess = newChatSession(s.col) // 每个浏览器会话一份历史
		s.sessions[id] = sess
	}
	return sess
}

func (s *server) handlePage(w http.ResponseWriter, r *http.Request) {
	if err := pageTmpl.Execute(w, nil); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
	}
}

func (s *server) handleAsk(w http.ResponseWriter, r *http.Request) {
	var req struct {
		SessionID string `json:"session_id"`
		Question  string `json:"question"`
	}
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil || req.Question == "" {
		http.Error(w, "bad request", http.StatusBadRequest)
		return
	}

	flusher, ok := w.(http.Flusher)
	if !ok {
		http.Error(w, "streaming unsupported", http.StatusInternalServerError)
		return
	}
	w.Header().Set("Content-Type", "text/event-stream")
	w.Header().Set("Cache-Control", "no-cache")

	send := func(v any) {
		b, _ := json.Marshal(v)
		fmt.Fprintf(w, "data: %s\n\n", b)
		flusher.Flush()
	}

	sess := s.sessionFor(req.SessionID)
	_, hits, _, err := sess.Ask(r.Context(), req.Question, func(delta string) {
		send(map[string]any{"type": "delta", "text": delta})
	})
	if err != nil {
		send(map[string]any{"type": "error", "message": err.Error()})
		return
	}

	sources := make([]string, 0, len(hits))
	seen := map[string]bool{}
	for _, h := range hits {
		label := h.Source
		if h.Title != "" {
			label += " › " + h.Title
		}
		if !seen[label] {
			seen[label] = true
			sources = append(sources, label)
		}
	}
	send(map[string]any{"type": "sources", "sources": sources})
	send(map[string]any{"type": "done"})
}

func serve(addr string) error {
	col, err := openCollection()
	if err != nil {
		return err
	}
	if col.Count() == 0 {
		return fmt.Errorf("索引是空的，先运行 build 建索引")
	}

	s := &server{col: col, sessions: map[string]*ChatSession{}}
	mux := http.NewServeMux()
	mux.HandleFunc("/", s.handlePage)
	mux.HandleFunc("/api/ask", s.handleAsk)

	srv := &http.Server{Addr: addr, Handler: mux}
	log.Printf("打开 http://localhost%s", addr)
	return srv.ListenAndServe()
}
```

在 `main.go` 里加：

```text
case "serve":
	fs := flag.NewFlagSet("serve", flag.ExitOnError)
	addr := fs.String("addr", ":8080", "监听地址")
	fs.Parse(os.Args[2:])
	must(serve(*addr))
```

### 7.3 跑起来

```bash
go run . serve
# 浏览器打开 http://localhost:8080
```

### 7.4 检查点

- 连续问 3 轮有上下文关联的问题，第三轮还能答对（浏览器刷新会换 `session_id`，历史随之清空——符合预期）。
- 回答是**一个字一个字蹦出来**的（SSE 流式生效）。
- 底部显示引用来源，复制路径能在仓库里搜到原文。

### 7.5 常见坑

| 现象 | 原因 | 处理 |
|------|------|------|
| 回答一次性全部出现 | 反代/中间层缓冲了 SSE | 本地直连不会出现；上 Nginx 要关 `proxy_buffering` |
| 端口被占用 | 8080 被别的程序用 | `go run . serve --addr :8090` |
| 多人用同一台机器互相串历史 | 会话按 `session_id` 隔离，但都在内存里 | 本机自用没问题；上线要加鉴权 + 持久化（见 `13.5 AI_SaaS架构`） |

---

## 8 步骤八：评测与调优

### 8.1 为什么必须做

没有评测的 RAG 调优就是玄学：改完 Prompt 感觉"好像好了点"，实际可能是这一题恰好蒙对。**先定基线，再改一个变量，再看数字。**

### 8.2 三类失败分开看

```text
问题 → [检索] → 上下文 → [生成] → 答案
        ↑ 失败1        ↑ 失败2/3
```

| 类型 | 症状 | 归因方法 | 对症下药 |
|------|------|----------|----------|
| 失败 1：召回没中 | 上下文里压根没有答案 | `go run . search` 看 Top-K | 换 embedding、调 chunk、加混合检索 |
| 失败 2：召回了但排序靠后 | 答案在第 8 名，`k=6` 捞不着 | 把 `k` 调大看答案排名 | 上 Rerank（`5.6`）、开 MMR |
| 失败 3：上下文有但答错 | 检索没问题，生成跑偏 | 人工对比上下文和答案 | 改 Prompt、换更强的 LLM |

### 8.3 eval.go：命中率评测

原理：给每个问题标好"答案应该在哪些文件里"，只看召回的块有没有覆盖这些文件。**这个指标不用人工打分，能自动化跑。**

```go
// rag_qa_bot_go/eval.go
package main

import (
	"context"
	"fmt"

	"github.com/philippgille/chromem-go"
)

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
```

在 `main.go` 里加：

```text
case "eval":
	fs := flag.NewFlagSet("eval", flag.ExitOnError)
	k := fs.Int("k", cfg.TopK, "评估用的 Top-K")
	fs.Parse(os.Args[2:])
	cmdEval(*k)
```

```go
func cmdEval(k int) {
	col, err := openCollection()
	must(err)
	requireIndex(col)
	requireAPIKey()
	must(runEval(col, k))
}
```

```bash
go run . eval
# ✅ k=6 RAG 和微调的区别是什么
# ...
# 命中率：9/10 = 90%
```

**基线目标**：先跑到 **≥ 80%**。低于这个数别急着调生成，先按 8.4 修检索。

### 8.4 按顺序调这四刀

每次只改一个，跑 `eval` 对比：

| 顺序 | 动作 | 预期效果 | 成本 |
|------|------|----------|------|
| 1 | `--k` 从 6 调到 10 | 失败 2 的题会回来 | 免费，上下文变长变贵 |
| 2 | `--rebuild` 重建索引：`CHUNK_SIZE` 调 1200 或剥掉代码块 | 代码类问题变好 | 几分钱 |
| 3 | 检索后加 Rerank：先召回 20 条，再用重排模型取 4 条（`5.6` 有原理和模型选型；Go 里调重排 API 或本地 ONNX） | 普遍 +5~15% | 延迟 +100ms 左右 |
| 4 | 混合检索：关键词（BM25）+ 向量并行召回再融合（`5.4`） | 专有名词、缩写类问题变好 | 需要自己实现一份 BM25 或引第三方库 |

### 8.5 生成质量的评测

检索命中率之外，答案本身好不好只能靠人评。20 题足够，每题打三个勾：

| 维度 | 合格标准 |
|------|----------|
| 忠实度 | 答案里每句结论都能在上下文里找到依据 |
| 完整性 | 覆盖了上下文里的关键点，没有漏 |
| 引用准确 | 标注的文件/小节确实包含该结论 |

想自动化可以看 `11.5 LLM评测体系` 里的 RAGAS 方案：用另一个 LLM 当裁判，自动算 `faithfulness` / `answer_relevancy` / `context_precision`。先在人工评测上把问题摸清楚，再决定要不要上。

---

## 9 收尾：代码清单与学习地图

### 9.1 你一共写了 9 个文件

| 文件 | 行数 | 职责 |
|------|------|------|
| `config.go` | 84 | 配置、LLM 客户端工厂 |
| `ingest.go` | 270 | 加载（含 CRLF 归一化）+ 两级切分 |
| `index.go` | 88 | 向量化、批量写入、重建 |
| `retrieve.go` | 120 | 检索、元数据过滤、MMR、余弦相似度 |
| `rag.go` | 178 | Prompt、上下文拼装、流式生成、追问改写、会话 |
| `eval.go` | 59 | 命中率评测 |
| `web.go` | 170 | HTTP + SSE 流式 Web UI |
| `main.go` | 238 | 命令入口（骨架见附录 D） |
| 合计 | **1216** | 门槛不在代码量，在切分、检索、评测这些"调"的地方 |

### 9.2 完整的运行顺序

```bash
cd rag_qa_bot_go
go run . check                        # 1. 连通性自检
go run . ingest                       # 2. 加载 + 切分统计（不花钱）
go run . build                        # 3. 建索引（文档变动后加 --rebuild）
go run . search "你的问题"             # 4. 调检索
go run . ask "你的问题"                # 5. 单轮问答（流式）
go run . chat                         # 6. 多轮对话
go run . eval                         # 7. 评测
go run . serve                        # 8. Web UI
```

### 9.3 下一步学什么（回仓库对应章节）

| 想深入 | 看这里 | Go 里怎么落地 |
|--------|--------|---------------|
| 切分策略的原理和对比 | `5.1 Chunk策略` | 扩展 `ingest.go` 的 `defaultSeparators` |
| 中文 embedding 怎么选 | `5.2 Embedding模型` | 换 `EMBEDDING_MODEL`（记得 `--rebuild`） |
| RAG 全流程每个环节 | `5.3 RAG_Pipeline` | 本文就是它的 Go 实现 |
| 查询重写、混合检索、语义缓存 | `5.4 RAG高级主题` | 改写已在 `rag.go`；BM25 可加一份内存索引 |
| GraphRAG、多跳推理 | `5.5 RAG高级架构` | 独立项目 |
| 重排序原理与 Cross-Encoder | `5.6 Rerank模型` | 调重排 API 或 ONNX Runtime Go 绑定 |
| 向量索引算法（HNSW/IVF/PQ） | `8.4 向量索引算法` | chromem 是暴力扫描；规模上来换 Milvus（附录 E） |
| 完整生产级 RAG（Docker 等） | `12.1 本地知识库RAG` | 思路通用，语言无关 |
| RAG 平台分层架构 | `13.2 RAG系统架构` | 把 web.go 拆成网关 + 检索服务 |
| 评测体系 | `11.5 LLM评测体系` | 扩展 `eval.go` |

---

## 附录 A 常见报错速查

| 报错 / 现象 | 原因 | 处理 |
|-------------|------|------|
| `401 Unauthorized` | Key 错、过期，或与 Base URL 不匹配 | 检查 `.env` 里 Key 和 `OPENAI_BASE_URL` 是否成对（中转 Key 配官方 URL 必报 401/404） |
| `404 Not Found` / `model_not_found` | 模型名在当前网关不存在 | 换网关支持的模型名；Ollama 用 `ollama list` 里已有的名字 |
| `context deadline exceeded` / 连接超时 | 网络或代理问题 | 检查 `HTTP_PROXY`/`HTTPS_PROXY`；或换 Base URL |
| `this model does not support temperature` | 推理型模型不接受 `temperature` 参数 | 把 `chatParams` 里的 `Temperature` 整行删掉（代价：少一个随机性旋钮） |
| 检索结果全是你没见过的向量 | 换过 embedding 模型但没重建 | `go run . build --rebuild` |
| `nResults must be <= ...` | `k` 超过集合大小 | 本文已自动钳制；自定义查询时注意 |
| `go: cannot find main module` | 不在 `rag_qa_bot_go/` 目录里执行命令 | `cd rag_qa_bot_go` 再跑 |
| `missing go.sum entry` | 依赖没下全 | `go mod tidy` |
| Windows 控制台中文乱码 | GBK 代码页 | `chcp 65001` |
| 回答全是"资料里没有提到" | 检索空手而归 | 先跑 `search` 定位是不是召回问题 |
| 回答流畅但引用对不上 | 幻觉 | 检查 Prompt 规则 1、3 是否被删改；`Temperature` 是否被调高 |

## 附录 B 零成本本地方案（Ollama）

不想花 API 钱，就本地跑。装 Ollama 后：

```bash
ollama pull qwen3:8b      # 生成用（按机器显存选，中文能力够用）
ollama pull bge-m3        # Embedding 用（1024 维，5.2 推荐的开放中文模型）
```

`.env` 改成：

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
LLM_MODEL=qwen3:8b
EMBEDDING_MODEL=bge-m3
```

然后 **`go run . build --rebuild`**（embedding 换模型必须重建），其余代码一行不动——chromem 的 OpenAI 兼容 Embedding 函数天然支持 Ollama。

取舍：

| | 云 API | 本地 Ollama |
|---|---|---|
| 成本 | 几分钱（索引）+ 每次问答微量 | 0 |
| 速度 | 快（受网络影响） | 取决于显卡，CPU 明显慢 |
| 隐私 | 文档内容上传 | 全本地 |
| 质量 | `gpt-5.4-mini` 级 | 8B 级，复杂问答差距明显 |

## 附录 C 参数速查表

| 参数 | 位置 | 默认 | 调大 | 调小 |
|------|------|------|------|------|
| `CHUNK_SIZE` | `.env` | 800 | 上下文更完整，精度下降 | 检索更准，易答不全 |
| `CHUNK_OVERLAP` | `.env` | 120 | 边界信息不易丢，块数变多 | 省成本，跨块论述易断 |
| `TOP_K` | `.env` | 6 | 召回率↑、噪声↑、更贵 | 精度↑、易漏 |
| `EMBED_CONCURRENCY` | `.env` | 8 | 建索引更快，易触发限流 | 保守 |
| `maxHistoryMessages` | `rag.go` | 6 | 记更久，token 更多 | 防跑偏，短期指代易丢 |
| `Temperature` | `rag.go` | 0 | 创意场景才调高 | — |
| MMR 的 `lambda` | `retrieve.go` 调用处 | 0.5 | 偏"相关" | 偏"多样" |

## 附录 D 完整 main.go 与"假 Embedding"离线测试

### D.1 main.go 骨架（各步骤拼装后的最终形态）

> 为省篇幅，命令处理函数体在各步骤里给出；这里只列骨架，方便你对照检查自己的 `main.go` 有没有拼对。（`cmdChat` 用到的 `bufio` 也见步骤六。）

```go
// rag_qa_bot_go/main.go（骨架）
package main

import (
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

func cmdIngest() { /* 见步骤二 */ }

func cmdSearch(question string, k int, chapter string, useMMR bool) { /* 见步骤四 */ }

func cmdAsk(question string) { /* 见步骤六 */ }

func cmdChat() { /* 见步骤六 */ }

func cmdEval(k int) { /* 见步骤八 */ }

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
```

### D.2 "假 Embedding"离线测试：不花一分钱验证链路

调参、改代码时不可能每次都调 API。用**确定性的假 Embedding**（字符袋 + 归一化）代替真模型，就能把"加载 → 切分 → 落盘 → 检索 → 过滤 → 上下文拼装"整条链路离线跑一遍。语义质量测不了，但**管道有没有漏、持久化能不能读回、过滤器有没有生效**全能测出来。

```go
// rag_qa_bot_go/offline_test.go
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
```

```bash
go test -run TestOfflinePlumbing ./...
# ok  	ragqabot	0.9s
```

这套测试在本仓库上实测通过——它也是本文所有非 API 代码的验证方式。

## 附录 E 换生产级向量库（Milvus / Qdrant / PGVector）

chromem-go 是嵌入式暴力扫描：几万块以内毫无压力，**上百万块或要并发服务时才需要换**。仓库对应章节：`8.2 Milvus向量数据库`、`8.3 向量数据库选型指南`、`8.5 PGVector`。Go 侧的官方/主流客户端：

| 向量库 | Go 客户端 | 适用 |
|--------|-----------|------|
| Milvus | `github.com/milvus-io/milvus-sdk-go/v2` | 分布式、亿级向量 |
| Qdrant | `github.com/qdrant/go-client` | 单机性能好、易运维 |
| PGVector | `github.com/pgvector/pgvector-go` | 已有 Postgres，想统一存储 |
| Weaviate | `github.com/weaviate/weaviate-go-client` | 自带混合检索 |

改造范围很小：只动 `index.go`（写入）和 `retrieve.go`（查询）里的存取逻辑，`Ingest → Chunk → Hit` 这些结构体和上层 `rag.go` / `web.go` 完全不用改——这也是为什么本文把 `Hit` 定义成自己的结构体，而不是直接把 chromem 的 `Result` 往上抛。

---

*最后更新：2026年9月17日*
