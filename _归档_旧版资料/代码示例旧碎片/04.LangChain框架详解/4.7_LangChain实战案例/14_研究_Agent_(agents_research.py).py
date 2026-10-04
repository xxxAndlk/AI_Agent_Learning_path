"""
研究 Agent
负责信息检索和知识收集
"""
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI

from .base import BaseAgent, AgentConfig


class ResearchAgent(BaseAgent):
    """研究 Agent"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[ChatOpenAI] = None,
    ):
        super().__init__(config, llm)
        self.search_results: List[Dict[str, Any]] = []
    
    def process(self, query: str) -> Dict[str, Any]:
        """
        研究查询内容
        
        Args:
            query: 研究查询
            
        Returns:
            研究结果
        """
        system_prompt = f"""{self.config.system_prompt}

你是一个研究专家。你的职责是：
1. 深入分析用户查询
2. 收集相关信息和背景知识
3. 提供全面的信息总结
4. 标注信息来源和可靠性

请提供详细的研究报告，包括：
- 背景信息
- 关键概念解释
- 相关技术和方法
- 最佳实践
- 潜在问题和挑战

用中文撰写，保持专业性和准确性。"""
        
        response = self.call_llm(query, system_prompt)
        
        result = {
            "query": query,
            "findings": response,
            "sources": [],
            "confidence": 0.8,
        }
        
        self.search_results.append(result)
        self.update_context("latest_research", result)
        
        return result
    
    def research_subtopic(self, subtopic: str) -> str:
        """研究子主题"""
        system_prompt = f"""{self.config.system_prompt}

请简洁地解释以下概念或问题：

{subtopic}

要求：
1. 用通俗易懂的语言解释
2. 提供关键要点
3. 如有代码示例，请一并提供
4. 限制在 200 字以内"""
        
        return self.call_llm(subtopic, system_prompt)
    
    def compare_options(
        self,
        options: List[str],
        criteria: List[str],
    ) -> Dict[str, Any]:
        """比较多个选项"""
        options_text = "\n".join(f"- {opt}" for opt in options)
        criteria_text = "\n".join(f"- {c}" for c in criteria)
        
        prompt = f"""请根据以下标准比较这些选项：

选项：
{options_text}

比较标准：
{criteria_text}

请提供详细的对比分析和推荐。"""
        
        system_prompt = f"""{self.config.system_prompt}

你是一个专业的比较分析专家。请提供客观、全面的分析。"""
        
        response = self.call_llm(prompt, system_prompt)
        
        return {
            "options": options,
            "criteria": criteria,
            "analysis": response,
        }
