package model

// ============================================
// 4. LLM 生成回答（DeepSeek Responses API 版）
// ============================================

// ResponsesRequest 对应 OpenAI Responses API 的请求格式
// DeepSeek V4 原生支持此格式，端点: POST https://api.deepseek.com/responses
// Instructions 相当于 system prompt，Input 相当于 user prompt
type ResponsesRequest struct {
	Model        string `json:"model"`        // 模型ID: deepseek-v4-pro 或 deepseek-v4-flash
	Instructions string `json:"instructions"` // 系统指令/角色设定
	Input        string `json:"input"`        // 用户输入（包含上下文+问题）
	Stream       bool   `json:"stream"`       // false = 一次性返回完整回答
}

// ResponsesResponse 对应 OpenAI Responses API 的响应格式
// 回答文本嵌套在 output[...].content[...].text 中
type ResponsesResponse struct {
	Output []struct {
		Type    string `json:"type"` // 通常为 "message"
		Content []struct {
			Type string `json:"type"` // 通常为 "output_text"
			Text string `json:"text"` // 模型生成的实际文本
		} `json:"content"`
	} `json:"output"`
}
