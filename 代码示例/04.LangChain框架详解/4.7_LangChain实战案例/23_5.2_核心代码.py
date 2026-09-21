"""
代码生成助手
"""
from typing import Optional, Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser


class CodeGenerator:
    """代码生成助手"""
    
    # 支持的语言
    SUPPORTED_LANGUAGES = [
        "python", "javascript", "typescript", "java",
        "go", "rust", "c", "cpp", "c#", "ruby",
        "php", "swift", "kotlin", "sql"
    ]
    
    def __init__(
        self,
        model_name: str = "gpt-5.4-mini",
        api_key: Optional[str] = None,
    ):
        self.llm = ChatOpenAI(model=model_name, api_key=api_key)
    
    def generate(
        self,
        requirement: str,
        language: str = "python",
        context: Optional[str] = None,
        framework: Optional[str] = None,
    ) -> str:
        """
        生成代码
        
        Args:
            requirement: 需求描述
            language: 编程语言
            context: 上下文信息
            framework: 框架（如 FastAPI, React 等）
            
        Returns:
            生成的代码
        """
        # 构建提示词
        prompt = self._build_prompt(requirement, language, context, framework)
        
        # 调用 LLM
        response = self.llm.invoke(prompt)
        
        return response.content
    
    def _build_prompt(
        self,
        requirement: str,
        language: str,
        context: Optional[str],
        framework: Optional[str],
    ) -> str:
        """构建提示词"""
        framework_info = f"，使用 {framework} 框架" if framework else ""
        
        prompt = f"""请生成 {language} 代码{framework_info}。

需求描述：
{requirement}

{"上下文信息：" + context if context else ""}

要求：
1. 代码完整、可运行
2. 遵循 {language} 的最佳实践
3. 添加必要的注释
4. 处理可能的异常情况

只返回代码，不要有其他解释。"""
        
        return prompt
    
    def explain(self, code: str, language: str = "python") -> str:
        """解释代码"""
        prompt = f"""请解释以下 {language} 代码：

```{language}
{code}
```

提供详细的解释，包括：
1. 代码的整体功能
2. 关键部分的说明
3. 可能的改进建议"""
        
        return self.llm.invoke(prompt).content
    
    def review(self, code: str, language: str = "python") -> Dict[str, Any]:
        """审查代码"""
        prompt = f"""请审查以下 {language} 代码：

```{language}
{code}
```

请提供：
1. 代码评分（1-10分）
2. 发现的问题
3. 改进建议"""
        
        response = self.llm.invoke(prompt).content
        
        return {
            "code": code,
            "review": response,
        }
    
    def refactor(
        self,
        code: str,
        language: str = "python",
        target_style: str = "clean",
    ) -> str:
        """重构代码"""
        prompt = f"""请将以下 {language} 代码重构为 {target_style} 风格：

```{language}
{code}
```

要求：
1. 保持功能不变
2. 提高代码可读性
3. 应用最佳实践

只返回重构后的代码。"""
        
        return self.llm.invoke(prompt).content


# 使用示例
if __name__ == "__main__":
    generator = CodeGenerator()
    
    # 生成代码
    code = generator.generate(
        requirement="创建一个函数，接受一个数字列表，返回平均值",
        language="python",
    )
    print("生成的代码：")
    print(code)
    
    # 解释代码
    print("\n代码解释：")
    explanation = generator.explain(code)
    print(explanation)
