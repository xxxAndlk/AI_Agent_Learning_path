# LLM应用架构示例

"""
典型LLM应用架构：

┌────────────────────────────────────────────────────────────┐
│                    LLM Application                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Client  │  │ API      │  │ LLM      │  │ Vector   │   │
│  │          │  │ Gateway  │  │ Service  │  │ Store    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└────────────────────────────────────────────────────────────┘
"""

class LLMApplication:
    """LLM应用主类"""
    
    def __init__(self, config: dict):
        """
        初始化LLM应用
        
        参数:
            config: 应用配置，包含API密钥、模型参数等
        """
        self.config = config
        self.llm_service = None
        self.vector_store = None
        
    def initialize(self):
        """初始化各组件"""
        # 初始化LLM服务
        self.llm_service = LLMService(
            api_key=self.config.get("api_key"),
            model=self.config.get("model", "gpt-5.4-mini")
        )
        
        # 初始化向量存储
        if self.config.get("use_rag"):
            self.vector_store = VectorStore(
                persist_directory=self.config.get("vector_db_path")
            )
        
    def process_request(self, user_input: str) -> str:
        """处理用户请求"""
        # 构建提示词
        prompt = self.build_prompt(user_input)
        
        # 如果启用RAG，先检索知识
        context = ""
        if self.vector_store:
            docs = self.vector_store.similarity_search(user_input, k=3)
            context = "\n\n".join([d.page_content for d in docs])
        
        # 调用LLM生成响应
        response = self.llm_service.generate(
            prompt=prompt,
            context=context
        )
        
        return response
    
    def build_prompt(self, user_input: str) -> str:
        """构建提示词"""
        return f"用户输入: {user_input}\n\n请给出有帮助的回答。"


class LLMService:
    """LLM服务封装"""
    
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        
    def generate(self, prompt: str, context: str = "") -> str:
        """生成响应"""
        full_prompt = f"上下文: {context}\n\n{prompt}" if context else prompt
        # 这里调用实际的LLM API
        # return openai.ChatCompletion.create(...)
        return "生成的响应"


class VectorStore:
    """向量存储封装"""
    
    def __init__(self, persist_directory: str):
        self.persist_directory = persist_directory
        
    def similarity_search(self, query: str, k: int = 3):
        """相似度搜索"""
        # 返回相关的文档
        return []


def main():
    """主函数"""
    # 配置
    config = {
        "api_key": "your-api-key",
        "model": "gpt-5.4-mini",
        "use_rag": True,
        "vector_db_path": "./vector_db"
    }
    
    # 创建应用
    app = LLMApplication(config)
    app.initialize()
    
    # 处理请求
    response = app.process_request("什么是机器学习？")
    print(response)


if __name__ == "__main__":
    main()
