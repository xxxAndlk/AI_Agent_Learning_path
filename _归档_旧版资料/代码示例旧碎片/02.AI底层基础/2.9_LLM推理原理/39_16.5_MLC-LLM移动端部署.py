"""
MLC-LLM移动端部署
支持iOS、Android、Web
"""

# MLC-LLM是一个编译器，支持将LLM部署到：
# - iOS (Metal)
# - Android (Vulkan/OpenCL)
# - Web (WebGPU)

# 1. 准备模型
"""
# 使用MLC-LLM工具链
mlc_llm convert_weight \
    --model meta-llama/Llama-2-7b-chat-hf \
    --quantization q4f16_1 \
    --output dist/llama-7b-chat-q4f16_1

# 生成配置文件
mlc_llm gen_config \
    --model meta-llama/Llama-2-7b-chat-hf \
    --quantization q4f16_1 \
    --conv_template llama3 \
    --output dist/llama-7b-chat-q4f16_1/mlc-chat-config.json
"""

# 2. 部署到iOS
# 参考: https://mlc.ai/mlc-llm/docs/deploy/ios.html

# iOS Swift使用示例:
"""
import MLCLLM

let config = MLCEngineConfig(model: "model", modelLib: "Llama-2-7b-chat-hf")
let engine = try await MLCEngine(config: config)

let response = try await engine.chat(
    messages: [MLCMessage(role: .user, content: "你好")]
)
print(response)
"""

# 3. 部署到Android
# 参考: https://mlc.ai/mlc-llm/docs/deploy/android.html

# Android Kotlin使用示例:
"""
val engine = MLCEngine.create("Llama-2-7b-chat-hf")
val response = engine.chat("你好")
Log.d("MLC-LLM", response)
"""

# 4. Web部署
# 参考: https://mlc.ai/mlc-llm/docs/deploy/web.html

# Web JavaScript使用示例:
"""
import * as mlc from '@mlc-ai/web-llm';

const engine = await mlc.CreateMLCEngine("Llama-2-7b-chat-hf");
const response = await engine.chat.completions.create({
    messages: [{role: "user", content: "你好"}]
});
console.log(response.choices[0].message.content);
"""
