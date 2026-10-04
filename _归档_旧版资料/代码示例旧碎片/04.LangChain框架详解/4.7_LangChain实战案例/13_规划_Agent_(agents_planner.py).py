"""
规划 Agent
负责分析任务并制定执行计划
"""
from typing import Any, Dict, List, Optional
from langchain_openai import ChatOpenAI

from .base import BaseAgent, AgentConfig, Message


class PlannerAgent(BaseAgent):
    """规划 Agent"""
    
    def __init__(
        self,
        config: AgentConfig,
        llm: Optional[ChatOpenAI] = None,
    ):
        super().__init__(config, llm)
        self.current_plan: Optional[Dict[str, Any]] = None
    
    def process(self, task: str) -> Dict[str, Any]:
        """
        分析任务并生成计划
        
        Args:
            task: 任务描述
            
        Returns:
            执行计划
        """
        system_prompt = f"""{self.config.system_prompt}

你是一个任务规划专家。你的职责是：
1. 分析用户请求，理解目标
2. 将复杂任务分解为可执行的子任务
3. 确定任务执行顺序和依赖关系
4. 为每个子任务指定合适的执行 Agent

请以 JSON 格式返回计划，格式如下：
{{
    "task": "原始任务描述",
    "goal": "任务目标",
    "subtasks": [
        {{
            "id": 1,
            "description": "子任务描述",
            "agent": "负责的 Agent 类型",
            "dependencies": [],
            "priority": "high/medium/low"
        }}
    ],
    "execution_order": [1, 2, 3],
    "estimated_time": "预计耗时"
}}

只返回 JSON，不要有其他内容。"""
        
        response = self.call_llm(task, system_prompt)
        
        try:
            import json
            # 尝试解析 JSON
            plan = self.parse_json_response(response)
            self.current_plan = plan
            self.update_context("plan", plan)
            return plan
        except Exception as e:
            # 返回简单计划
            return {
                "task": task,
                "goal": "完成用户任务",
                "subtasks": [
                    {
                        "id": 1,
                        "description": task,
                        "agent": "research",
                        "dependencies": [],
                        "priority": "high"
                    }
                ],
                "execution_order": [1],
            }
    
    def parse_json_response(self, response: str) -> Dict[str, Any]:
        """解析 JSON 响应"""
        import json
        import re
        
        # 尝试提取 JSON
        json_match = re.search(r'\{[\s\S]*\}', response)
        if json_match:
            return json.loads(json_match.group())
        
        raise ValueError("无法解析 JSON")
    
    def can_proceed(self, subtask_id: int) -> bool:
        """检查是否可以执行某个子任务"""
        if not self.current_plan:
            return False
        
        subtask = next(
            (s for s in self.current_plan["subtasks"] if s["id"] == subtask_id),
            None
        )
        
        if not subtask:
            return False
        
        # 检查依赖
        for dep_id in subtask.get("dependencies", []):
            dep_status = self.get_context(f"subtask_{dep_id}_status")
            if dep_status != "completed":
                return False
        
        return True
    
    def update_subtask_status(self, subtask_id: int, status: str):
        """更新子任务状态"""
        self.update_context(f"subtask_{subtask_id}_status", status)
