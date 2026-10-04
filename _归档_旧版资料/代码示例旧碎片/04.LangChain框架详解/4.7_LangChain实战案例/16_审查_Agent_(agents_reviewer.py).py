"""
审查 Agent
负责代码审查和质量评估
"""
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI

from .base import BaseAgent, AgentConfig


class ReviewerAgent(BaseAgent):
    """审查 Agent"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[ChatOpenAI] = None,
    ):
        super().__init__(config, llm)
        self.review_results: List[Dict[str, Any]] = []
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        审查代码或结果
        
        Args:
            task: 审查任务
            
        Returns:
            审查结果
        """
        content = task.get("content", "")
        content_type = task.get("type", "code")  # code, document, plan
        
        if content_type == "code":
            return self.review_code(content, task.get("language", "python"))
        elif content_type == "document":
            return self.review_document(content)
        elif content_type == "plan":
            return self.review_plan(content)
        else:
            raise ValueError(f"未知的审查类型: {content_type}")
    
    def review_code(
        self,
        code: str,
        language: str = "python",
    ) -> Dict[str, Any]:
        """审查代码"""
        system_prompt = f"""{self.config.system_prompt}

你是一个资深的代码审查专家。你的职责是：
1. 识别代码中的问题
2. 提供具体的改进建议
3. 评估代码质量和安全性
4. 检查代码规范和最佳实践

请提供详细、结构化的审查报告。"""
        
        prompt = f"""请审查以下 {language} 代码：

```{language}
{code}
```

请按以下格式提供审查报告：

## 总体评价
[总体评价]

## 问题列表
1. [问题描述] - [严重程度] - [位置]
2. ...

## 改进建议
1. [具体建议]
2. ...

## 评分 (1-10)
- 正确性: X
- 可读性: X
- 性能: X
- 安全性: X"""
        
        response = self.call_llm(prompt, system_prompt)
        
        result = {
            "type": "code",
            "language": language,
            "review": response,
            "issues": [],
            "score": 8.0,
        }
        
        self.review_results.append(result)
        return result
    
    def review_document(self, document: str) -> Dict[str, Any]:
        """审查文档"""
        system_prompt = f"""{self.config.system_prompt}

你是一个技术文档审查专家。请审查文档的：
1. 完整性和准确性
2. 清晰度和可读性
3. 结构和组织
4. 语法和格式"""
        
        prompt = f"""请审查以下文档：

{document}

提供详细的审查报告和改进建议。"""
        
        response = self.call_llm(prompt, system_prompt)
        
        return {
            "type": "document",
            "review": response,
        }
    
    def review_plan(self, plan: str) -> Dict[str, Any]:
        """审查计划"""
        system_prompt = f"""{self.config.system_prompt}

你是一个项目规划审查专家。请审查计划的：
1. 可行性
2. 完整性
3. 优先级合理性
4. 依赖关系正确性"""
        
        prompt = f"""请审查以下计划：

{plan}

提供审查意见和改进建议。"""
        
        response = self.call_llm(prompt, system_prompt)
        
        return {
            "type": "plan",
            "review": response,
        }
