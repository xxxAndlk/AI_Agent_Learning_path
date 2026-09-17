package main

import (
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"strings"
	"unicode/utf8"
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

// ---------- 切分：第一级按 Markdown 标题 ----------

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

// ---------- 切分：第二级递归字符切分（按 rune 计数，对中文友好）----------

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
