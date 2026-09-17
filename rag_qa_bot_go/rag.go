package main

import (
	"context"
	"errors"
	"fmt"
	"strings"

	"github.com/openai/openai-go"
	"github.com/philippgille/chromem-go"
)

const systemPrompt = `你是「AI 应用开发技术栈」学习资料的答疑助手。

规则：
1. 只依据 <上下文> 回答。上下文里没有的信息，直接说「资料里没有提到」，不要凭常识补充，更不要编造。
2. 用中文回答，尽量具体：参数、结论、代码要点都从上下文里取，别泛泛而谈。
3. 每个关键结论后用 [来源: 文件路径 › 小节标题] 标注出处，最多标 3 处。
4. 如果多个文档结论有冲突，指出冲突并分别标注来源。
5. 回答末尾用一句话说明「依据的是哪几个小节」，方便读者回查。`

const condensePrompt = `根据对话历史，把用户的最新问题改写成一个不依赖上文、可独立检索的完整问题。
只输出改写后的问题，不要解释。若最新问题本身已完整，原样返回，不要画蛇添足。`

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

func printHitsShort(hits []Hit) {
	for i, h := range hits {
		line := fmt.Sprintf("  [%d] %s", i+1, h.Source)
		if h.Title != "" {
			line += " › " + h.Title
		}
		fmt.Println(line)
	}
}
