# RAG 实战课程：手写一个文档问答机器人（Go）

> 这是一份**教学课程**，不是代码仓库。每一步只给：目标、知识点、要写的函数（签名+职责）、关键 API、易错点、验收检查点。
> **代码全部由你自己写**。卡住时先看本步的「实现提示」和「易错点」，再去查 `go doc`。
> 学完的成果：一个能对**本仓库的 Markdown** 提问、带 `[来源: …]` 引用回答的机器人，有命令行 + 网页两个界面。

## 1 课程说明

### 1.1 最终形态

命令行：

```bash
go run . ingest                          # 统计知识库规模
go run . build --rebuild                 # 全量建向量索引
go run . search "chunk 怎么切"            # 只检索，不调用大模型
go run . ask "chunk_overlap 取多少？"      # 完整问答，带引用
go run . chat                            # 多轮对话
go run . serve                           # 网页版（流式输出）
go run . eval                            # 10 道题的命中率评估
```

网页版：浏览器里聊天，回答一个字一个字蹦出来。

### 1.2 技术栈

| 用途 | 选型 | 版本 | 为什么 |
| --- | --- | --- | --- |
| LLM / Embedding | [openai/openai-go](https://github.com/openai/openai-go) | v1.12.0 | OpenAI 官方 Go SDK；走 OpenAI 兼容协议，中转网关 / Ollama / vLLM 通吃 |
| 向量库 | [philippgille/chromem-go](https://github.com/philippgille/chromem-go) | v0.7.0 | 纯 Go、零依赖、嵌入式，数据落盘成文件；几千条规模毫秒级检索 |
| 环境变量 | [joho/godotenv](https://github.com/joho/godotenv) | v1.5.1 | 本地开发读 `.env` |
| Web | 标准库 `net/http` + `html/template` + SSE | — | 不需要框架 |

> 为什么不上 Milvus/Qdrant：学习阶段先跑通全链路。数据量上百倍后再换，接口心智一样（见附录 E）。

### 1.3 前置条件

- Go 1.22+（开发环境 1.25），`GOPROXY` 正常
- 一个 OpenAI 兼容的 API Key（官方或中转；想全本地跑看附录 B 的 Ollama）
- 会 Go 基础语法即可；并发只用到 `sync.Mutex`，不用自己写 goroutine

### 1.4 学习方法（重要）

每步都按同一结构展开：

| 小节 | 内容 |
| --- | --- |
| 目标 | 做完这一步应能跑出什么 |
| 知识点 | 为什么这么设计——面试也会问 |
| 函数清单 | 要写哪些函数、签名、职责，实现留给你 |
| API 速查 | 官方库函数的确切签名，可直接抄 |
| 易错点 | 真实踩过的坑，能省你几小时 |
| 检查点 | 跑什么命令、期望看到什么。**不通过不要进下一步** |

节奏：自己写 → 跑检查点 → 通过再往下。检查点都是"可执行的真话"，不通过说明前面有 bug，不要带病前进。

### 1.5 目录结构（写完全部约 1200 行 Go）

```
rag_qa_bot_go/          # 项目在本仓库内，目录名与 .gitignore 条目一致
├── .env                # API Key（不入库）
├── go.mod
├── main.go             # ~240 行  子命令入口
├── config.go           # ~80 行   配置加载
├── ingest.go           # ~270 行  加载 + 两级切分
├── index.go            # ~90 行   向量化 + 入库
├── retrieve.go         # ~120 行  检索 + MMR
├── rag.go              # ~180 行  提示词 + 生成 + 多轮
├── eval.go             # ~60 行   命中率评估
├── web.go              # ~170 行  Web UI + SSE
└── data/               # 向量库落盘（自动生成，不入库）
```

## 2 总大纲

| 步骤 | 内容 | 主要文件 | 验收命令 |
| --- | --- | --- | --- |
| 第 0 步 | 项目初始化：module、依赖、.env | go.mod / .env | `go list -m all` |
| 第 1 步 | 配置 + 连通性检查 | config.go / main.go 骨架 | `go run . check` |
| 第 2 步 | 加载与两级切分 | ingest.go | `go run . ingest` |
| 第 3 步 | Embedding 与建索引 | index.go | `go run . build --rebuild` |
| 第 4 步 | 检索（先不接大模型） | retrieve.go | `go run . search "…"` |
| 第 5 步 | 生成 + 来源引用 | rag.go | `go run . ask "…"` |
| 第 6 步 | 多轮对话 + 查询改写 | rag.go | `go run . chat` |
| 第 7 步 | Web UI + SSE 流式 | web.go | `go run . serve` |
| 第 8 步 | 命中率评估 | eval.go | `go run . eval` |
| 第 9 步 | 收尾与进阶路线 | — | `git status` |

依赖关系：0→1→2→3→4→5 是严格顺序；6、7 依赖 5；8 依赖 4。

## 3 第 0 步：项目初始化

**目标**：空项目能编译、依赖就位、`.env` 建好。预计 20 分钟。

**任务清单**

1. 在仓库根目录建项目目录 `rag_qa_bot_go/`（仓库 `.gitignore` 里已有对应条目），进去执行 `go mod init ragqabot`
2. 拉依赖（版本按本课来，别随手用 latest）：

   ```bash
   go get github.com/openai/openai-go@v1.12.0
   go get github.com/philippgille/chromem-go@v0.7.0
   go get github.com/joho/godotenv@v1.5.1
   ```

3. 写 `.env`（四个变量）：

   ```
   OPENAI_API_KEY=sk-你的key
   OPENAI_BASE_URL=https://api.openai.com/v1
   LLM_MODEL=gpt-5.4-mini
   EMBEDDING_MODEL=text-embedding-3-small
   ```

4. 仓库根 `.gitignore` 确认包含（Key 和向量库数据都不入库）：

   ```
   rag_qa_bot_go/.env
   rag_qa_bot_go/data/
   ```

**知识点**

- **Go module**：`go.mod` 锁依赖版本，`go.sum` 锁内容哈希，换机器 `go mod download` 即还原。
- **为什么 .env 不入库**：Key 泄露 = 别人拿你的钱包刷。没有例外。
- **OpenAI 兼容协议**：仓库根目录下的所有主流供应商（中转网关、Ollama、vLLM）实现的是同一套 HTTP 接口，所以只要代码里 BASE_URL 可配，换供应商不用改一行代码。这是后面反复受益的设计。

**易错点**

- 依赖拉不动：设 `GOPROXY=https://goproxy.cn,direct`（国内镜像）
- **别把 SDK 搞混**：网上大量教程用的是 `sashabaranov/go-openai`（包名也叫 `openai`）。本课用的是**官方** `github.com/openai/openai-go`（v1.x）。两者 API 完全不同，抄错版本编译报错
- `.env` 建好后用 `git status` 看一眼，确认它没出现在待提交列表里

**检查点**

```bash
go list -m all | grep -E "openai-go|chromem-go|godotenv"
```

三个依赖都出现即通过。

## 4 第 1 步：配置与连通性检查

**目标**：`go run . check` 能读到配置、发出第一条 LLM 请求并打印回复。预计 1~2 小时。

**知识点**

- **配置从环境变量来**（12-factor）：`godotenv` 只是本地开发时把 `.env` 加载进进程环境；生产直接给环境变量，代码不用改。
- **项目目录定位**：`go run` 的可执行文件在临时目录，而 cwd 是仓库根——`data/`、`.env` 都在**源码目录**旁边。所以路径不能相对 cwd 算，要用 `runtime.Caller(0)` 取当前源文件路径再推目录。这是开发期技巧，正式分发要换成 `os.Executable()`。
- **知识库在项目外一层**：`RepoRoot = 项目目录的上一级`（即仓库根）。切分器要扫的是仓库的章节目录，不是项目目录。
- **最小验证优先**：在写任何复杂功能前，先证明"Key 有效、网络通、SDK 用得对"。`check` 子命令就是这个保险丝。

**函数清单**

`config.go`：

| 函数/类型 | 签名 | 职责 |
| --- | --- | --- |
| `Config` | `type Config struct { APIKey, BaseURL, LLMModel, EmbeddingModel, ProjectDir, RepoRoot, DataDir string }` | 全局配置载体 |
| `loadConfig` | `func loadConfig() (*Config, error)` | 定位项目目录 → `godotenv.Load(项目目录/.env)`（文件不存在**不算错误**）→ `os.Getenv` 读取，空值给默认（`gpt-5.4-mini` / `text-embedding-3-small`）→ 推导 `RepoRoot`（上一级）、`DataDir`（项目目录/data） |
| `newLLMClient` | `func newLLMClient() openai.Client` | 用 APIKey + BaseURL 构造客户端 |

> 提示：给 `RepoRoot` 留一个 `KNOWLEDGE_ROOT` 环境变量覆盖口，以后换知识库目录不用改代码。

`main.go`：

| 函数 | 职责 |
| --- | --- |
| `main()` | 取 `os.Args[1]` 分发子命令；每个子命令一个 `flag.NewFlagSet`；本步先实现 `check`，其余留桩 |
| `cmdCheck(cfg)` | 发一条"只回复 ok"的请求，打印模型回复与模型名 |
| `must(err)` / `requireAPIKey(cfg)` | 出错即退出；Key 为空时给明确提示（而不是等 401） |

**API 速查**（openai-go v1.x）

```go
client := openai.NewClient(
    option.WithAPIKey(cfg.APIKey),
    option.WithBaseURL(cfg.BaseURL),
)

resp, err := client.Chat.Completions.New(ctx, openai.ChatCompletionNewParams{
    Model: openai.ChatModel("gpt-5.4-mini"), // 底层类型就是 string
    Messages: []openai.ChatCompletionMessageParamUnion{
        openai.UserMessage("只回复 ok"),
    },
})
// 回复文本：
resp.Choices[0].Message.Content // string
```

查签名：`go doc github.com/openai/openai-go.ChatCompletionNewParams`。

**易错点**

- **BaseURL 填到 `/v1` 为止**：SDK 自己拼 `/chat/completions`；你自己再拼一层就会 404
- **消息不是结构体字面量**：`Messages` 的元素是 union 类型，要用构造函数 `openai.SystemMessage(...)` / `openai.UserMessage(...)` / `openai.AssistantMessage(...)`，不要手写嵌套结构
- **`godotenv.Load` 传绝对路径**（项目目录拼出来的）；cwd 不对时它会静默失败，表现为 Key 为空 → 401
- **模型名走环境变量**，别硬编码：换模型/网关只动 `.env`
- 有的中转网关对缺省 `temperature` 敏感，本课从第 5 步起统一显式给 `0`

**检查点**

```bash
go run . check
```

期望：打印模型回复（如 `ok`）与模型名。再故意把 `.env` 里 Key 改错一位重跑，期望看到清晰的 401 报错——错误能透出，说明链路真实。

## 5 第 2 步：加载与切分

**目标**：`go run . ingest` 扫描仓库，把 Markdown 切成带元数据的块，打印统计。预计 3~5 小时（本课最重的一步）。

**知识点**

- **RAG 第一性**：检索的最小单元是 chunk。chunk 质量决定整个系统的上限——切碎了检索不到，切大了噪声多还费 token。
- **两级切分**：
  1. **按 Markdown 标题切小节**（`#` / `##` / `###`）——标题是作者划好的语义边界，白送的；
  2. **小节仍超长 → 递归字符切分**：按分隔符优先级 `\n## ` → `\n### ` → 空行 → 换行 → `。` → `；` → `，` → 空格 → 字符，在"最像自然边界"的地方断开。
- **为什么用 rune 计数**：中文 1 个字是 3 个 UTF-8 字节。用 `len()` 是按字节算，长度差 3 倍，还可能把一个汉字切成半个（非法 UTF-8）。**一切长度计算用 `utf8.RuneCountInString`**。
- **overlap 的意义**：相邻块共享一小段尾巴，防止答案正好被切在边界上；代价是索引略大。
- **确定性 ID**：`文件相对路径#小节序号#块序号`。好处：重建索引幂等（同 ID 覆盖）、检索结果可追溯。
- **知识库范围（本课规则）**：仓库根下所有 `.md`，**排除** `README.md` 和 `修改记录_` 开头的文件；另外跳过点开头目录（`.git` 等）和本项目目录。

**函数清单**（全部写在 `ingest.go`）

| 函数/类型 | 签名 | 职责 |
| --- | --- | --- |
| `Doc` | `type Doc struct { Path, Chapter, Text string }` | 一篇文档：相对仓库根路径（正斜杠）、一级目录名、全文 |
| `Chunk` | `type Chunk struct { ID, Source, Chapter, H1, H2, Content string; Index int }` | 一个块 + 溯源元数据 |
| `loadDocs` | `func loadDocs(root string) ([]Doc, error)` | `filepath.WalkDir` 遍历；按规则过滤；`os.ReadFile`；**CRLF→LF 归一化** |
| `splitByHeaders` | `func splitByHeaders(text string) []section` | 逐行扫描切小节，维护代码围栏开关 |
| `section` | `type section struct { H1, H2, Body string }` | 一个小节 |
| `splitRecursive` | `func splitRecursive(text string, size, overlap int, seps []string) []string` | 递归切分超长文本 |
| `hardSplit` | `func hardSplit(text string, size, overlap int) []string` | 无分隔符可用的兜底：按 rune 硬切 |
| `chunkDoc` | `func chunkDoc(d Doc) []Chunk` | 串起来：切小节 → 递归切 → 过滤太短 → 编 ID 与元数据 |
| `cmdIngest` | `func cmdIngest(cfg *Config) error` | 打印统计与抽样块 |

常量与工具：`chunkSize = 800`、`chunkOverlap = 120`、`minChunkRunes = 40`、`defaultSeparators`（优先级如上）；工具函数 `runeLen`、`firstRunes`、`tailRunes`、`titleOf`（生成 `H1 › H2` 标题串）。

**`splitRecursive` 实现提示**（文字级，代码自己写）

- 取当前优先级最高的分隔符尝试切分；每段 ≤ size 直接收下；仍超长的段 → 去掉当前分隔符、用剩余分隔符列表递归切。
- 分隔符会被 `strings.Split` 吃掉——用 `strings.SplitAfter`（分隔符留在段尾）或切前替换成带标记的形式，否则标题行全丢，引用时块的开头看不懂。
- 逐段累积时长度按 rune 算，封顶 size；overlap 的实现：新块开头先取上一块尾部 overlap 个 rune 作为上下文。
- 递归到底（分隔符列表耗尽）仍超长 → `hardSplit` 兜底。
- **不变量：每块长度 ≤ size + overlap**。检查点会验它。
- 先断言 `overlap < size`，且每次推进至少消耗 1 个 rune——否则递归不推进，栈溢出。

**API 速查**

```go
filepath.WalkDir(root string, fn fs.WalkDirFunc) error // fn 里用 d.IsDir() 判断，return filepath.SkipDir 跳过目录
os.ReadFile(path string) ([]byte, error)
strings.ReplaceAll(s, "\r\n", "\n")   // CRLF 归一化
utf8.RuneCountInString(s) int         // 长度一律用它
[]rune(s) / string(rs)                // 按 rune 切片
strings.Split / SplitAfter / HasPrefix / HasSuffix / TrimSpace / Contains
```

**易错点**

- **`len()` 计中文**：块数虚高、块长虚大 3 倍。切分逻辑里出现 `len(s)` 都要怀疑
- **CRLF**：Windows 下读出来行尾带 `\r`。不归一化，字符统计会多出约等于行数的量（实测差过 11 万字符），块内容里藏 `\r` 还影响 embedding 质量
- **代码围栏**：文档代码块里的 `# 注释` / `## xx` 会被误判成标题 → 用"行首三反引号翻转"的 `inFence` 状态跳过围栏内所有行
- **排除名单**：`README.md`、`修改记录_` 前缀、点开头目录、本项目目录。漏一个，统计数字就对不上
- **太短的块**：< 40 rune 的基本是切分残留，直接过滤（否则检索结果里全是 `|`、`---` 这类噪声）
- **元数据用正斜杠相对路径**（`05.RAG系统（重点）/5.1_Chunk策略.md`），别用 Windows 反斜杠——引用展示、评估匹配都靠它
- **第一个标题之前的正文**别丢，归到"前言"节或并入第一节

**检查点**

```bash
go run . ingest
```

期望统计（本课程在真实仓库上测得，你的数字应基本一致）：

- **80 个文件 / 2,960,826 字符 / 8242 个块**
- 每块长度：min = 40、avg ≈ 431、max ≈ 917（≈ chunkSize + overlap）

数字不对的排查顺序：文件数不对 → 排除规则；字符数偏大且块内有 `\r` → CRLF；块数远多于 8242 → 围栏/小节切分失效；max 超 920 → overlap 叠加逻辑写重了。

再抽查前 3 个块：ID 形如 `05.RAG系统（重点）/5.1_Chunk策略.md#3#0`，元数据含 `source/chapter/h1/h2`，块尾断在句号或段落处。

## 6 第 3 步：建索引

**目标**：`go run . build --rebuild` 把 8000 多个块向量化并落盘。预计 1~2 小时写代码 + 跑 3~8 分钟。

**知识点**

- **Embedding**：把文本映射成固定长度向量（`text-embedding-3-small` 是 **1536 维**），语义相近的文本在向量空间距离近。这是"用自然语言检索"的根基。
- **chromem-go 的持久化实现**（v0.7.0）：每个文档一个 gob 文件、同步写。8000 多个块 = 8000 多次文件写 → 建索引慢的主因在磁盘，不在 API。
- **EmbeddingFunc 不会被序列化**：重开数据库时必须传入与建库时相同的 EmbeddingFunc，chromem 只能靠你保证一致。
- **幂等**：ID 确定性 → 同 ID 重复添加是覆盖。但**换 embedding 模型必须 `--rebuild`**：向量空间变了（维度都可能不同），新旧向量混在一起检索没有意义。
- **成本**：约 300 万字符 ≈ 100 万 token 量级 ≈ **几美分**。先跑 `ingest` 看规模，再决定跑 `build`。

**函数清单**（`index.go`）

| 函数 | 签名 | 职责 |
| --- | --- | --- |
| `embeddingFunc` | `func embeddingFunc() chromem.EmbeddingFunc` | 用 chromem 内置的 OpenAI 兼容构造器，baseURL / key / model 来自 cfg |
| `openDB` | `func openDB() (*chromem.DB, error)` | `NewPersistentDB(cfg.DataDir, false)` |
| `openCollection` | `func openCollection(db *chromem.DB) (*chromem.Collection, error)` | `GetOrCreateCollection("docs", nil, embeddingFunc())` |
| `buildIndex` | `func buildIndex(rebuild bool) error` | rebuild → `os.RemoveAll(DataDir)`；loadDocs → chunkDoc → 分批（64 块）`AddDocuments(ctx, batch, 8)`；打印进度 |
| `cmdBuild` | `func cmdBuild(cfg *Config, rebuild bool)` | flag：`--rebuild` |

**API 速查**

```go
chromem.NewPersistentDB(path string, compress bool) (*chromem.DB, error)
db.GetOrCreateCollection(name string, metadata map[string]string, ef chromem.EmbeddingFunc) (*chromem.Collection, error)
col.AddDocuments(ctx context.Context, docs []chromem.Document, concurrency int) error
col.Count() int

chromem.NewEmbeddingFuncOpenAICompat(baseURL, apiKey, model string, normalized *bool) chromem.EmbeddingFunc
// normalized 传 nil：首次请求自动探测（OpenAI 的向量本身已归一化，不用我们处理）

chromem.Document{ID: string, Metadata: map[string]string, Content: string} // Embedding 字段留给库自己填
```

**易错点**

- **并发不是越大越好**：`AddDocuments` 的 concurrency 传 8；出现 429 降到 4；超过 16 基本只会触发限流
- **中断留半成品**：Ctrl+C 后 data/ 里是部分索引；下次先 `--rebuild`
- **换模型不重建**：改了 `EMBEDDING_MODEL` 或 `OPENAI_BASE_URL` 后必须 `--rebuild`
- **进度要打印**：几千个块的批量任务不给进度等于盲跑，每批打一行 `i/total`
- `data/` 目录路径用 `filepath.Join(cfg.ProjectDir, "data")`；确认在 `.gitignore` 里（第 0 步已加）

**检查点**

```bash
go run . build --rebuild     # 进度到 8242/8242，无报错，3~8 分钟（并发 8）
go run . build               # 不带 rebuild：很快跑完（同 ID 覆盖），证明幂等
ls data/docs | wc -l         # ≈ 8243（8242 个块 + 1 个元数据文件）
```

## 7 第 4 步：检索（先不接大模型）

**目标**：`go run . search "chunk_size 和 overlap 怎么取"` 打印 top-k（分数+来源+预览），肉眼判断相关性。预计 1~2 小时。

**知识点**

- **余弦相似度**：chromem 全量扫描算相似度，几千条毫秒级。规模到百万级再换 HNSW 类索引（Milvus/Qdrant），现在暴力扫就是最优解。
- **为什么先做纯检索**：RAG 调优一半时间花在检索上。这一步只花一次 query embedding 的钱（可忽略），可以随便试。
- **元数据过滤**：`where` 按建库时写的元数据筛（如 `chapter`），实现"限定章节内搜索"。注意是**精确匹配**。
- **MMR（最大边际相关性）**：top-k 常常全是同一节的相邻块（内容重复）。MMR 先取 `fetchK = 20` 个候选，贪心选 k 个：第一个取最相似的，之后每次最大化 `λ×相似度 − (1−λ)×与已选块的最大相似度`（λ = 0.5）。结果更"散"，覆盖更多角度。
- **v0.7.0 的便利**：`Query` 返回的 `Result` **自带 `Embedding` 字段**（源码里回填了），MMR 不用再取向量。另外 `GetByID`（按 ID 精确取文档）是调试神器，值得知道。

**函数清单**（`retrieve.go`）

| 函数/类型 | 签名 | 职责 |
| --- | --- | --- |
| `Hit` | `type Hit struct { ID, Source, Chapter, Title, Content string; Score float32 }` | 检索结果 |
| `searchIndex` | `func searchIndex(ctx, col, query string, k int, chapter string) ([]Hit, error)` | 调 `col.Query`；k 先夹紧到 `col.Count()`；chapter 非空 → 构造 where |
| `mmrSearch` | `func mmrSearch(ctx, col, query string, k, fetchK int, lambda float64) ([]Hit, error)` | Query 取 fetchK 个 → 贪心 MMR 选 k 个 |
| `cosine` | `func cosine(a, b []float32) float64` | 归一化向量的点积 |
| `printHits` | `func printHits(hits []Hit)` | 序号 / 分数 / 来源 / 前 100 rune 预览 |

`main.go` 加 `cmdSearch`：flags `--k`（默认 5）、`--chapter`。

**API 速查**

```go
col.Query(ctx context.Context, queryText string, nResults int, where, whereDocument map[string]string) ([]chromem.Result, error)
// where / whereDocument 为 map[string]string 精确匹配，不需要时传 nil
chromem.Result{ID, Metadata map[string]string, Content string, Embedding []float32, Similarity float32}
col.GetByID(ctx context.Context, id string) (chromem.Document, error)
```

**易错点**

- **`nResults` 必须 ≤ `col.Count()`**，否则报 `nResults must be <= the number of documents in the collection`。空库/小库上最容易撞 → 先夹紧：k 超过 Count 就取 Count
- **`where` 是精确匹配**：传 `"RAG"` 匹配不到 `"05.RAG系统（重点）"`，要传完整值
- 过滤后 0 条命中返回空切片（不是错误）——上层要处理"没检索到"
- 首次查询要加载 gob 文件，会慢一两秒；同进程后续查询毫秒级
- k 建议 4~6：太小漏召回，太大给第 5 步的 prompt 塞噪声

**检查点**

```bash
go run . search "chunk_size 和 overlap 怎么取"                # top1 来源应为 05.RAG系统（重点）/5.1_Chunk策略.md
go run . search "余弦相似度" --k 5                             # 5 条都应和向量/相似度相关
go run . search "怎么建索引" --chapter "05.RAG系统（重点）"      # 只返回该章的块
```

**进阶（可选，练测试手艺）**：写 `offline_test.go`——用"字符袋 + 归一化"造一个假 embedding 函数（不花 API 钱、不依赖网络），灌 2 条文档，断言：持久化重开后 `Count() == 2`、检索能命中预期块、上下文拼装的来源头格式正确。`go test ./...` 通过。

## 8 第 5 步：生成与来源引用

**目标**：`go run . ask "文档里 chunk_overlap 建议取多少？"` 输出带 `[来源: 文件 › 小节]` 的回答；问知识库外的问题，回答"资料里没有提到"。预计 1~2 小时。

**知识点**

- **上下文拼装**：把检索到的块拼成一段文本，每块前面加 `[来源 › 标题]` 头。模型看到来源，才有东西可引用。
- **系统提示词四要素**（自己写，别抄——写的过程就是学习）：
  1. 只根据提供的资料回答；
  2. 资料里没有 → 明确说"资料里没有提到"，禁止编造；
  3. 每条结论标注 `[来源: 文件路径 › 小节]`，最多 3 个；
  4. 用中文回答，直接回答不啰嗦。
- **temperature = 0**：事实型问答要稳定复现，不要创造性。
- **幻觉防线**：宁可回答"不知道"。RAG 系统的信任是一次性资产，编造一次就废了。

**函数清单**（`rag.go`）

| 函数/常量 | 签名 | 职责 |
| --- | --- | --- |
| `systemPrompt` | `const systemPrompt = ...` | 上面四要素 |
| `buildContext` | `func buildContext(hits []Hit) string` | `[来源 › 标题]` + 内容 + 分隔线，逐块拼接 |
| `chatParams` | `func chatParams(model, system, user string) openai.ChatCompletionNewParams` | 统一构造请求参数（含 `Temperature: openai.Float(0)`） |
| `generate` | `func generate(ctx, client, question string, hits []Hit) (string, error)` | 一次非流式调用；`len(resp.Choices) == 0` 要返回错误 |
| `printHitsShort` | `func printHitsShort(hits []Hit)` | 回答后打印本次引用到的来源清单 |

`main.go` 加 `cmdAsk`：`--k`、`--chapter`，同 search。

**API 速查**

```go
openai.ChatCompletionNewParams{
    Model: openai.ChatModel("gpt-5.4-mini"),
    Messages: []openai.ChatCompletionMessageParamUnion{
        openai.SystemMessage(systemPrompt),
        openai.UserMessage("资料：\n" + buildContext(hits) + "\n\n问题：" + question),
    },
    Temperature: openai.Float(0), // 注意：不是裸 float
}
```

**易错点**

- **`Temperature` 是 `param.Opt[float64]`**：必须 `openai.Float(0)`；直接写 `0` 编译不过
- **别把 hits 忘了传**：忘了就是裸聊模型——症状是回答很流畅但一个 `[来源]` 都没有
- **prompt 里声明的来源格式要和 `buildContext` 一字不差**，否则模型引用的格式五花八门
- 拼 user 消息时"资料在前、问题在后"对指令遵循更稳
- k 越大 prompt 越长：k=5 × 800 rune ≈ 2~3k token，安全；k=20 就 10k+ 了，成本和噪声都要掂量

**检查点**

```bash
go run . ask "文档里 chunk_overlap 建议取多少？"   # 回答含 [来源: …5.1_Chunk策略…]，数字与文档一致
go run . ask "今天上海天气怎么样"                  # 回答"资料里没有提到"——防幻觉生效
go run . ask "RAG 是什么？" --k 1                 # 对比 k=1 和默认 k=5 的回答质量差
```

引用里出现的文件、小节要真实存在于仓库——抽查验证。

## 9 第 6 步：多轮对话

**目标**：`go run . chat` 连续问答；第二轮问"那 overlap 呢？"也能检索到正确的文件。预计 2 小时。

**知识点**

- **指代问题**：多轮里用户说"那它默认多少？"——这句话单独拿去检索什么都检索不到，必须先把"它"还原成"chunk_overlap"。
- **查询改写（Condense）**：让 LLM 结合历史把最新问题改写成**独立问题**；用独立问题去**检索**，用原始问题去**生成**（生成时模型看到自然语气的问题）。
- **历史窗口**：只带最近 6 条消息。历史越长 prompt 越贵，且旧话题会干扰检索。

**函数清单**（都在 `rag.go`）

| 函数 | 签名 | 职责 |
| --- | --- | --- |
| `condensePrompt` | `const condensePrompt = ...` | 要求：结合对话历史，把新问题改写成不依赖上下文的完整问题；只输出改写结果，不要回答 |
| `rewriteQuery` | `func rewriteQuery(ctx, client, history []openai.ChatCompletionMessageParamUnion, question string) string` | 无历史 → 原样返回；调用失败 → **回退原问题**（改写失败不能阻断主流程） |
| `ChatSession` | `type ChatSession struct { History []openai.ChatCompletionMessageParamUnion }` | 会话状态 |
| `(*ChatSession) Ask` | `func (s *ChatSession) Ask(ctx, client, col, question string, k int) (string, []Hit, error)` | 改写 → 检索 → 生成 → 追加历史（只存 user + assistant 文本） |
| `trimHistory` | `func trimHistory(s *ChatSession, max int)` | 超过 6 条从最老的砍 |
| `cmdChat` | `func cmdChat(cfg *Config) error` | `bufio.Scanner` 读 stdin 循环，`exit` 退出 |

**易错点**

- **检索用改写问题、生成用原问题**——顺序别反，反了指代会很怪
- **历史只存文本消息**：不要把上一轮的检索上下文重复塞进历史（prompt 爆炸且会误导）
- **改写调用同样 temperature = 0**，并打印改写结果（调试开关），否则你无法判断检索为什么没命中
- 裁剪历史从最老开始，尽量保持 user/assistant 交替（有些网关对消息交替敏感）
- 改写提示词要明确"只输出改写后的问题，不要回答它"，否则模型直接开始答题

**检查点**

```
$ go run . chat
> chunk 怎么切比较好？
（回答…）
> 那 overlap 呢？        ← 检索应命中 5.1_Chunk策略.md（而不是检索不到或乱命中）
```

## 10 第 7 步：Web UI 与流式输出

**目标**：`go run . serve --addr :8080`，浏览器聊天，回答逐字出现。预计 2~3 小时。

**知识点**

- **SSE（Server-Sent Events）**：`Content-Type: text/event-stream`，每条消息一行 `data: {...}`、以空行结尾；单向推送，聊天够用，比 WebSocket 简单一个数量级。
- **流式生成**：SDK 的 `NewStreaming` 返回迭代器——`Next()` 前进、`Current()` 取块、`Err()` 查错、用完 `Close()`。
- **会话**：`map[sessionID]*ChatSession` 存在内存；浏览器用 `localStorage` 存 sessionID，刷新不丢上下文。

**函数清单**（`web.go`）

| 函数/常量 | 职责 |
| --- | --- |
| `pageHTML` | 单页：消息区 + 输入框；`fetch('/api/ask')` 拿流，`getReader()` + `TextDecoder` 读，按空行切事件，解析 `data:` 里的 JSON。注意**事件可能被 read 边界切成两半**，要缓冲区累积 |
| `server` | `struct { cfg *Config; llm openai.Client; col *chromem.Collection; mu sync.Mutex; sessions map[string]*ChatSession }` |
| `(*server) handleAsk` | 解析 JSON `{session_id, question}` → 取/建会话 → 设 SSE 响应头 → `generateStream` 的 `onDelta` 里写 `data: {"type":"delta","text":"…"}` 并 Flush → 收尾发 `sources` 与 `done` 事件 |
| `generateStream` | `func generateStream(ctx, client, question string, hits []Hit, onDelta func(string)) (string, error)` — 迭代 `NewStreaming`，每块拼全文 + 回调 |
| `serve` | `http.HandleFunc` 两个路由：`/` 页面、`/api/ask`；`http.ListenAndServe(addr, mux)` |

`main.go` 加 `cmdServe`：`--addr`（默认 `:8080`），先 `requireIndex` 再 `requireAPIKey`。

**API 速查**

```go
stream := client.Chat.Completions.NewStreaming(ctx, params) // *ssestream.Stream[openai.ChatCompletionChunk]
for stream.Next() {
    chunk := stream.Current()
    // chunk.Choices[0].Delta.Content 是增量文本；首块 Choices 可能为空，判 len
}
if err := stream.Err(); err != nil { /* 处理 */ }
defer stream.Close()

w.Header().Set("Content-Type", "text/event-stream")
w.Header().Set("Cache-Control", "no-cache")
flusher, _ := w.(http.Flusher)
flusher.Flush() // 每写完一条事件就 Flush
```

**易错点**

- **不 Flush = 没有流式**：全被缓冲到请求结束才吐出，页面表现是"转圈半天然后整段出现"
- **SSE 事件必须以空行结尾**（空行是消息边界）；只写一个换行，前端永远收不到完整事件
- **响应头发出后不能再 `http.Error`**：出错改成往流里写 `{"type":"error"}` 事件
- **把 `r.Context()` 一路传给 SDK**：用户关页面/刷新 → 请求取消 → API 调用停止，不烧钱、不泄漏
- **sessions 读写要加锁**：多个浏览器同时聊，map 并发写直接 panic（concurrent map writes）
- **别暴露公网**：没有鉴权、没有限流，本课定位是本机学习工具；上线前先补这两样
- 浏览器端别用 `EventSource`（不好发 POST），用 `fetch` + 手动切分

**检查点**

- 打开 `http://localhost:8080` 提问：文字**逐个出现**（不是整段弹出）
- F12 → Network → `api/ask` 是 `text/event-stream`，能看到一条条 data
- 连问两轮（含"那它呢？"）→ 多轮生效
- 刷新页面继续问 → 上下文还在（localStorage 里的 sessionID）
- 开两个标签页各聊各的 → 不串台、不崩

## 11 第 8 步：命中率评估

**目标**：`go run . eval` 输出 10 道题的检索命中率。预计 1~2 小时。

**知识点**

- **没有度量就没有优化**：调 chunk 大小、k、MMR 前后，需要一个数字告诉你"变好了还是变坏了"。
- **hit@k 定义**：每道题，top-k 里命中"期望来源文件"就算过。粗，但有效。
- **失败样本的价值**：失败题逐个看 top3，判断根因——内容被切碎（切分问题）还是语义鸿沟（检索问题），这两类修法完全不同。

**函数清单**（`eval.go`）

| 函数/类型 | 职责 |
| --- | --- |
| `evalCase` | `struct { Question, ExpectFile string }` |
| `evalCases` | 10 条：每章挑 1~2 题，覆盖概念题（"RAG 的流程是什么"）和事实题（"chunk_size 默认多少"） |
| `runEval` | `func runEval(ctx, col *chromem.Collection, k int) error` — 逐题 `searchIndex`，任一命中 `Source == ExpectFile` 记 ✅，最后打印 `命中 x/10` |
| `cmdEval` | 挂到 main.go 子命令 |

**易错点**

- **`ExpectFile` 与 `Source` 必须逐字符一致**（中文括号、正斜杠、目录前缀都在内），差一个字符永远不命中
- **题目别照抄文档标题**："5.1 Chunk策略"这种题测的是字符串匹配不是语义；要写口语问法，比如"文档切太大有什么坏处？"
- 评估每次会调一次 embedding（成本可忽略），但别放到 CI 定时跑

**检查点**

```bash
go run . eval
```

命中率 ≥ 7/10 算通过。失败题看 top3：命中文件不对但内容相关 → 切分/元数据问题；完全无关 → 查询写法或切分问题。

## 12 第 9 步：收尾与进阶路线

**收尾清单**

- `go run . build --rebuild` 做一次干净的最终索引
- `git status` 确认 `.env`、`data/` 没有被跟踪
- 项目里写个简短 README：命令速查 + 你的实测数字（文件数/块数/命中率）
- 评估题留下来——以后每次改切分参数都重跑一次，防回归

**进阶路线（按性价比排序）**

1. **Rerank**：检索 20 个候选 → 用 rerank 模型（Cohere / BGE-reranker）精排取 5，通常 +5~15% 命中，改动小
2. **混合检索**：BM25 关键词 + 向量，用 RRF 融合；专治"专有名词检索不到"（向量模型对罕见词弱）
3. **父子块**：小块检索（精度高）、命中后返回其父块（上下文全）
4. **换真向量库**：Milvus / Qdrant / PGVector（附录 E 有 Go 客户端），接口心智迁移成本低
5. **Agent 化**：把 search 包装成工具，接入 Agent 循环（见本仓库 Agent 章节）
6. **评估升级**：LLM-as-judge 打"忠实度 / 相关性 / 覆盖度"（RAGAS 思路），比 hit@k 细

## 附录 A 常见错误速查表

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| 401 Unauthorized | Key 错 / `.env` 没加载 / 网关不认 | 打印 Key 前 6 位确认加载了；用 `go run . check` 单点验证 |
| `nResults must be <= the number of documents` | k 没夹紧 | k 超过 `col.Count()` 就取 Count |
| 字符统计比预期大 ~10 万 | CRLF 没归一化 | 读文件后统一替换成 `\n` |
| 块数远多于 8242 | 围栏没管 / 排除名单失效 | 打印被排除的文件清单核对 |
| 回答完全没引用 | 没把 hits 传给 generate / 提示词没要求引用 | 打印发出去的 prompt 检查 |
| 回答流畅但和文档无关 | 同上（模型在裸聊） | 同上 |
| 页面转半天整段出字 | 没 Flush / SSE 缺空行结尾 | 见第 7 步易错点 |
| 块长度统计怪 | 用 `len()` 当 rune 用了 | 全换 `utf8.RuneCountInString` |
| 429 Too Many Requests | 并发过高 | AddDocuments 并发 8 → 4 |
| 检索 top-k 全是同一节 | 没有多样性 | 上 MMR（λ=0.5，fetchK=20） |
| 报 collection not found / 空结果 | 没建索引 | 先 `go run . build` |
| 改了 embedding 模型后结果变差 | 新旧向量混库 | `--rebuild` 重建 |

## 附录 B 全本地：换 Ollama

1. 装 Ollama，拉模型：`ollama pull qwen3:8b`（对话）、`ollama pull bge-m3`（embedding，中文效果好）
2. `.env` 改成：

   ```
   OPENAI_API_KEY=ollama
   OPENAI_BASE_URL=http://localhost:11434/v1
   LLM_MODEL=qwen3:8b
   EMBEDDING_MODEL=bge-m3
   ```

3. **必须 `go run . build --rebuild`**（embedding 空间换了：bge-m3 是 1024 维）
4. 代码零改动——这就是第 1 步"BASE_URL 可配"设计的回报

## 附录 C 参数速查

| 参数 | 取值 | 说明 |
| --- | --- | --- |
| chunkSize | 800 rune | 中文技术文档经验值；判断标准 = 一块能否完整说清一个知识点 |
| chunkOverlap | 120 rune | 15%；太小切断句子，太大索引冗余 |
| minChunkRunes | 40 | 更短的块直接过滤 |
| embedding 维度 | 1536（text-embedding-3-small） | 换模型必须重建索引 |
| temperature | 0 | 事实问答要稳定 |
| AddDocuments 并发 | 8 | 429 就降到 4 |
| 检索 k | 4~6 | 进 prompt 的块数 |
| MMR fetchK / λ | 20 / 0.5 | 候选数 / 相关性-多样性权衡 |
| 历史窗口 | 6 条消息 | 多轮对话 |
| 成本参考 | 全量索引 ≈ 300 万字符 ≈ 100 万 token ≈ 几美分 | 单次问答约 1~2 分钱 |

## 附录 D 每步验收总表

| 步骤 | 命令 | 期望 |
| --- | --- | --- |
| 0 | `go list -m all \| grep -E "openai-go\|chromem-go\|godotenv"` | 3 个依赖都在 |
| 1 | `go run . check` | 打印模型回复；Key 错时 401 |
| 2 | `go run . ingest` | 80 文件 / 2,960,826 字符 / 8242 块 |
| 3 | `go run . build --rebuild` | 进度 8242/8242；`data/docs` 下约 8243 个文件 |
| 4 | `go run . search "chunk_size 和 overlap 怎么取"` | top1 = 5.1_Chunk策略.md |
| 5 | `go run . ask "chunk_overlap 建议取多少？"` | 带 `[来源: …]`；库外问题答"没有提到" |
| 6 | `go run . chat` 二轮问"那 overlap 呢？" | 二轮检索命中 5.1 |
| 7 | `go run . serve` + 浏览器 | 逐字流出；event-stream |
| 8 | `go run . eval` | 命中 ≥ 7/10 |

## 附录 E 什么时候该换向量库

chromem-go 的适用边界：**单机、十万级块以内**——因为它是全量暴力扫描 + 每次写盘。

Go 客户端可迁移的目标：

| 库 | Go 客户端 | 适合 |
| --- | --- | --- |
| Milvus | `github.com/milvus-io/milvus/client/v2/milvusclient` | 百万级以上、分布式 |
| Qdrant | `github.com/qdrant/go-client` | 单机性能好、运维简单 |
| PostgreSQL + pgvector | `github.com/pgvector/pgvector-go` | 已有 PG、想少一个组件 |

迁移时只有"建索引/检索"两层要改，切分、提示词、评估原样复用——这也是为什么本课把它们分层实现。

## 总结

- RAG = 加载 → 切分 → 向量化 → 存储 → 检索 → 生成，每层都可独立调试；
- 最重的功夫在切分与检索（第 2、4 步），提示词只是最后一公里；
- 每条设计都对应一个坑：rune 计数、CRLF、代码围栏、k 夹紧、SSE Flush、查询改写回退；
- 检查点即验收：每步的数字对得上，最后一步才有意义。做完可以在评估集上继续调参，或按进阶路线加 rerank / 混合检索。
