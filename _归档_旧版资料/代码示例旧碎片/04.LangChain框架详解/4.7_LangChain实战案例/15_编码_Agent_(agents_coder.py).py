"""
编码 Agent
负责代码生成和实现
"""
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI

from .base import BaseAgent, AgentConfig


class CoderAgent(BaseAgent):
    """编码 Agent"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[ChatOpenAI] = None,
    ):
        super().__init__(config, llm)
        self.generated_code: List[Dict[str, Any]] = []
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成代码
        
        Args:
            task: 任务描述，包含 requirements 和 context
            
        Returns:
            生成的代码
        """
        requirements = task.get("requirements", "")
        language = task.get("language", "python")
        context = task.get("context", "")
        
        system_prompt = f"""{self.config.system_prompt}

你是一个专业的程序员。你的职责是：
1. 理解需求并设计合理的代码结构
2. 编写高质量、可维护的代码
3. 添加必要的注释和文档
4. 遵循最佳实践和编码规范

编程语言: {language}

请生成完整的、可运行的代码。"""
        
        prompt = f"""需求描述：
{requirements}

相关上下文：
{context}

请生成代码实现。"""
        
        code = self.call_llm(prompt, system_prompt)
        
        result = {
            "task": requirements,
            "language": language,
            "code": code,
            "status": "generated",
        }
        
        self.generated_code.append(result)
        self.update_context("latest_code", result)
        
        return result
    
    def generate_function(
        self,
        func_name: str,
        params: List[str],
        return_type: str,
        description: str,
        language: str = "python",
    ) -> str:
        """生成单个函数"""
        params_str = ", ".join(params)
        
        prompt = f"""请生成一个 {language} 函数：

函数名: {func_name}
参数: {params_str}
返回类型: {return_type}
描述: {description}

只返回代码，不要有其他解释。"""
        
        return self.call_llm(prompt, self.config.system_prompt)
    
    def explain_code(self, code: str, language: str = "python") -> str:
        """解释代码"""
        prompt = f"""请解释以下 {language} 代码的功能：

```{language}
{code}
```

请提供：
1. 整体功能描述
2. 关键部分说明
3. 可能的改进建议"""
        
        return self.call_llm(prompt, self.config.system_prompt)
    
    def review_code(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """审查代码"""
        prompt = f"""请审查以下 {language} 代码：

```{language}
{code}
```

请从以下方面进行审查：
1. 代码正确性
2. 性能问题
3. 安全漏洞
4. 代码规范
5. 潜在 bug

请提供详细的审查报告和改进建议。"""
        
        response = self.call_llm(prompt, self.config.system_prompt)
        
        return {
            "code": code,
            "review": response,
            "issues": [],
            "suggestions": [],
        }
