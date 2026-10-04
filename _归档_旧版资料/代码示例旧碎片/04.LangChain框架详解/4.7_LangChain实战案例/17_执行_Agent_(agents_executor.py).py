"""
执行 Agent
负责执行任务并返回结果
"""
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI

from .base import BaseAgent, AgentConfig


class ExecutorAgent(BaseAgent):
    """执行 Agent"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[ChatOpenAI] = None,
    ):
        super().__init__(config, llm)
        self.execution_history: List[Dict[str, Any]] = []
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task: 任务描述
            
        Returns:
            执行结果
        """
        task_type = task.get("type", "general")
        
        if task_type == "code":
            return self.execute_code(task)
        elif task_type == "research":
            return self.execute_research(task)
        elif task_type == "analysis":
            return self.execute_analysis(task)
        else:
            return self.execute_general(task)
    
    def execute_code(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行代码任务"""
        code = task.get("code", "")
        language = task.get("language", "python")
        
        # 模拟代码执行（实际使用时可以使用沙箱环境）
        result = {
            "status": "simulated",
            "code": code,
            "language": language,
            "output": f"[模拟执行] {language} 代码",
            "success": True,
        }
        
        self.execution_history.append(result)
        return result
    
    def execute_research(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行研究任务"""
        query = task.get("query", "")
        
        system_prompt = f"""{self.config.system_prompt}

你是一个研究执行专家。请根据查询提供有价值的信息。"""
        
        findings = self.call_llm(query, system_prompt)
        
        result = {
            "status": "completed",
            "query": query,
            "findings": findings,
        }
        
        self.execution_history.append(result)
        return result
    
    def execute_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行分析任务"""
        data = task.get("data", "")
        
        prompt = f"""请分析以下数据并提供见解：

{data}"""
        
        analysis = self.call_llm(prompt, self.config.system_prompt)
        
        return {
            "status": "completed",
            "analysis": analysis,
        }
    
    def execute_general(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行通用任务"""
        instruction = task.get("instruction", "")
        
        response = self.call_llm(instruction, self.config.system_prompt)
        
        return {
            "status": "completed",
            "result": response,
        }
    
    def get_execution_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.execution_history
