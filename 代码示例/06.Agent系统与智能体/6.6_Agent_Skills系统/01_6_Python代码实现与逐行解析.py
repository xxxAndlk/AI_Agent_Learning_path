"""
Agent Skills系统实现
展示如何构建可扩展的技能系统
"""

# 导入类型提示和抽象基类所需的模块
from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod  # ABC用于创建抽象基类，abstractmethod用于定义抽象方法
from dataclasses import dataclass, field  # dataclass简化数据类的创建，field用于配置字段
import json  # JSON序列化
import inspect  # 反射和自省，用于提取函数签名信息

# ============ 数据结构定义 ============

@dataclass
class SkillContext:
    """技能执行上下文 - 用于在技能执行过程中传递共享信息"""
    agent_memory: Dict = field(default_factory=dict)  # Agent共享内存，存储长期信息
    session_id: str = ""  # 当前会话标识，用于区分不同会话
    user_id: str = ""  # 当前用户标识
    metadata: Dict = field(default_factory=dict)  # 额外元数据

@dataclass
class SkillResult:
    """技能执行结果 - 标准化所有技能的执行返回格式"""
    success: bool  # 执行是否成功
    data: Any  # 执行返回的数据
    message: str = ""  # 执行结果的描述信息
    error: Optional[str] = None  # 错误信息（如果执行失败）
    execution_time: float = 0.0  # 执行耗时（秒）
    tokens_used: int = 0  # 使用的token数量（用于成本跟踪）

# ============ 技能基类 ============

class BaseSkill(ABC):
    """技能基类 - 所有具体技能都继承自此类"""
    
    def __init__(self):
        # 获取当前类的名称作为技能名称
        self.name = self.__class__.__name__
        # 获取类的文档字符串作为技能描述
        self.description = self.__doc__ or ""
        # 从execute方法提取参数定义
        self.parameters = self._extract_parameters()
    
    def _extract_parameters(self) -> Dict:
        """从execute方法提取参数定义"""
        # 获取execute方法的花名册（签名）
        sig = inspect.signature(self.execute)
        params = {}
        # 遍历所有参数
        for name, param in sig.parameters.items():
            if name == 'context':
                # 跳过context参数（这是所有技能都有的）
                continue
            # 构建参数信息字典
            param_info = {
                "type": "string",  # 简化处理，实际应该根据param.annotation获取
                "description": "",  # 参数描述
                "required": param.default == inspect.Parameter.empty  # 是否有默认值
            }
            params[name] = param_info
        return params
    
    @abstractmethod
    def execute(self, context: SkillContext, **kwargs) -> SkillResult:
        """执行技能 - 抽象方法，子类必须实现"""
        pass
    
    def validate_params(self, params: Dict) -> bool:
        """验证参数 - 检查必需参数是否都提供了"""
        # 找出所有必需的参数
        required_params = [
            k for k, v in self.parameters.items()
            if v.get("required", False)
        ]
        # 检查所有必需参数是否都在传入的params中
        return all(p in params for p in required_params)
    
    def to_dict(self) -> Dict:
        """转换为字典 - 用于序列化或API返回"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }

# ============ 核心技能实现 ============

class MemorySkill(BaseSkill):
    """
    记忆技能
    管理短期和长期记忆
    """
    
    def __init__(self):
        super().__init__()  # 调用父类初始化
        self.short_term_memory: List[Dict] = []  # 短期记忆（会话级）
        self.long_term_memory: Dict[str, Any] = {}  # 长期记忆（持久化）
    
    def execute(self, context: SkillContext, action: str, key: str = "", value: Any = None) -> SkillResult:
        """
        执行记忆操作
        
        参数:
            action: 操作类型 (store/recall/clear)
            key: 记忆键
            value: 记忆值
        """
        try:
            if action == "store":
                # 存储到长期记忆（需要key）或短期记忆
                if key:
                    self.long_term_memory[key] = value
                else:
                    self.short_term_memory.append(value)
                return SkillResult(success=True, data=None, message="记忆已存储")
            
            elif action == "recall":
                # 检索记忆
                if key:
                    data = self.long_term_memory.get(key)
                    return SkillResult(success=True, data=data, message="记忆已检索")
                else:
                    return SkillResult(success=True, data=self.short_term_memory, message="短期记忆已检索")
            
            elif action == "clear":
                # 清除记忆
                if key:
                    self.long_term_memory.pop(key, None)
                else:
                    self.short_term_memory.clear()
                return SkillResult(success=True, data=None, message="记忆已清除")
            
            else:
                return SkillResult(success=False, data=None, error=f"未知操作: {action}")
                
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))

class PlanningSkill(BaseSkill):
    """
    规划技能
    将复杂任务分解为可执行的子任务
    """
    
    def execute(self, context: SkillContext, task: str, steps: int = 5) -> SkillResult:
        """
        规划任务
        
        参数:
            task: 任务描述
            steps: 期望的步骤数
        """
        try:
            # 简化实现，实际应调用LLM进行智能分解
            plan = {
                "task": task,
                "steps": [
                    f"步骤{i+1}: 执行子任务{i+1}"
                    for i in range(steps)
                ],
                "estimated_time": f"{steps * 2}分钟"
            }
            
            return SkillResult(
                success=True,
                data=plan,
                message=f"任务'{task}'已分解为{steps}个步骤"
            )
            
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))

class ReflectionSkill(BaseSkill):
    """
    反思技能
    评估执行结果并提取经验教训
    """
    
    def execute(self, context: SkillContext, action: str, result: str) -> SkillResult:
        """
        反思执行
        
        参数:
            action: 执行的动作
            result: 执行结果
        """
        try:
            # 简化实现，实际应调用LLM进行深度反思
            reflection = {
                "action": action,
                "result": result,
                "success": "成功" in result or "完成" in result,
                "lessons": [
                    "执行过程中的经验1",
                    "可以改进的方面"
                ],
                "suggestions": [
                    "下次可以尝试的方法"
                ]
            }
            
            return SkillResult(
                success=True,
                data=reflection,
                message="反思完成"
            )
            
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))

# ============ 领域技能实现 ============

class CodeGenerationSkill(BaseSkill):
    """
    代码生成技能
    根据需求生成代码
    """
    
    def execute(self, context: SkillContext, language: str, requirement: str) -> SkillResult:
        """
        生成代码
        
        参数:
            language: 编程语言
            requirement: 代码需求描述
        """
        try:
            # 简化实现，实际应调用LLM生成真实代码
            code = f"""# {language}代码
# 需求: {requirement}

def generated_function():
    # 根据需求生成的代码
    pass
"""
            
            return SkillResult(
                success=True,
                data={"language": language, "code": code},
                message=f"已生成{language}代码"
            )
            
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))

class DataAnalysisSkill(BaseSkill):
    """
    数据分析技能
    分析数据并生成报告
    """
    
    def execute(self, context: SkillContext, data: List[Dict], analysis_type: str = "summary") -> SkillResult:
        """
        分析数据
        
        参数:
            data: 数据列表
            analysis_type: 分析类型 (summary/statistics/trend)
        """
        try:
            if analysis_type == "summary":
                # 汇总分析
                result = {
                    "total_records": len(data),
                    "fields": list(data[0].keys()) if data else [],
                    "sample": data[:3] if data else []
                }
            elif analysis_type == "statistics":
                # 统计分析
                result = {"record_count": len(data)}
            else:
                result = {"data": data}
            
            return SkillResult(
                success=True,
                data=result,
                message=f"{analysis_type}分析完成"
            )
            
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))

class WebSearchSkill(BaseSkill):
    """
    网络搜索技能
    搜索网络信息
    """
    
    def execute(self, context: SkillContext, query: str, num_results: int = 5) -> SkillResult:
        """
        搜索
        
        参数:
            query: 搜索查询
            num_results: 结果数量
        """
        try:
            # 模拟搜索结果（实际应调用真实搜索引擎API）
            results = [
                {"title": f"结果{i+1}", "url": f"https://example.com/{i}", "snippet": f"关于'{query}'的相关内容{i+1}"}
                for i in range(num_results)
            ]
            
            return SkillResult(
                success=True,
                data={"query": query, "results": results},
                message=f"找到{num_results}个结果"
            )
            
        except Exception as e:
            return SkillResult(success=False, data=None, error=str(e))

# ============ Skill管理器 ============

class SkillManager:
    """技能管理器 - 负责所有技能的生命周期管理"""
    
    def __init__(self):
        """初始化技能管理器"""
        self.skills: Dict[str, BaseSkill] = {}  # 存储所有注册技能
        self.skill_history: List[Dict] = []  # 记录技能执行历史
        self._register_builtin_skills()  # 注册内置技能
    
    def _register_builtin_skills(self):
        """注册内置技能 - 系统启动时自动注册"""
        builtin_skills = [
            MemorySkill(),
            PlanningSkill(),
            ReflectionSkill(),
            CodeGenerationSkill(),
            DataAnalysisSkill(),
            WebSearchSkill()
        ]
        
        for skill in builtin_skills:
            self.register_skill(skill)
    
    def register_skill(self, skill: BaseSkill) -> bool:
        """
        注册技能
        
        参数:
            skill: 技能实例
        """
        if skill.name in self.skills:
            print(f"⚠️ 技能'{skill.name}'已存在，将被覆盖")
        
        self.skills[skill.name] = skill
        print(f"✅ 技能已注册: {skill.name}")
        return True
    
    def unregister_skill(self, skill_name: str) -> bool:
        """注销技能 - 从管理器中移除技能"""
        if skill_name in self.skills:
            del self.skills[skill_name]
            print(f"✅ 技能已注销: {skill_name}")
            return True
        return False
    
    def get_skill(self, skill_name: str) -> Optional[BaseSkill]:
        """获取技能 - 根据名称返回技能实例"""
        return self.skills.get(skill_name)
    
    def list_skills(self) -> List[str]:
        """列出所有技能 - 返回技能名称列表"""
        return list(self.skills.keys())
    
    def execute_skill(
        self,
        skill_name: str,
        context: SkillContext,
        **params
    ) -> SkillResult:
        """
        执行技能
        
        参数:
            skill_name: 技能名称
            context: 执行上下文
            **params: 技能参数
        """
        skill = self.get_skill(skill_name)
        if not skill:
            return SkillResult(
                success=False,
                data=None,
                error=f"技能'{skill_name}'不存在"
            )
        
        # 验证参数
        if not skill.validate_params(params):
            return SkillResult(
                success=False,
                data=None,
                error="参数验证失败"
            )
        
        # 执行技能
        import time
        start_time = time.time()
        
        result = skill.execute(context, **params)
        
        execution_time = time.time() - start_time
        result.execution_time = execution_time
        
        # 记录历史
        self.skill_history.append({
            "skill": skill_name,
            "params": params,
            "result": result.success,
            "time": execution_time
        })
        
        return result
    
    def compose_skills(self, skill_chain: List[tuple], context: SkillContext) -> SkillResult:
        """
        组合执行多个技能
        
        参数:
            skill_chain: 技能链列表，格式为 [(skill_name, params), ...]
            context: 执行上下文
        """
        results = []
        
        for skill_name, params in skill_chain:
            result = self.execute_skill(skill_name, context, **params)
            results.append(result)
            
            # 如果某个技能执行失败，停止执行后续技能
            if not result.success:
                return SkillResult(
                    success=False,
                    data=results,
                    error=f"技能'{skill_name}'执行失败"
                )
        
        return SkillResult(
            success=True,
            data=results,
            message=f"成功执行{len(skill_chain)}个技能"
        )

# ============ Agent Skills集成 ============

class SkillsEnabledAgent:
    """支持技能的Agent - 整合技能系统的Agent实现"""
    
    def __init__(self):
        """初始化Agent"""
        self.skill_manager = SkillManager()  # 创建技能管理器
        self.context = SkillContext()  # 创建执行上下文
    
    def use_skill(self, skill_name: str, **params) -> SkillResult:
        """使用技能 - 代理到SkillManager的执行方法"""
        return self.skill_manager.execute_skill(skill_name, self.context, **params)
    
    def plan_and_execute(self, task: str) -> SkillResult:
        """规划并执行任务 - 展示技能组合的使用模式"""
        # 1. 规划
        plan_result = self.use_skill("PlanningSkill", task=task)
        if not plan_result.success:
            return plan_result
        
        plan = plan_result.data
        print(f"\n📋 任务规划:")
        for step in plan["steps"]:
            print(f"  - {step}")
        
        # 2. 执行（简化演示）
        # 实际应根据计划选择合适的技能执行
        
        # 3. 反思
        reflection = self.use_skill(
            "ReflectionSkill",
            action="plan_and_execute",
            result=f"任务'{task}'已规划"
        )
        
        return SkillResult(
            success=True,
            data={"plan": plan, "reflection": reflection.data},
            message="任务规划完成"
        )

# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建Agent
    agent = SkillsEnabledAgent()
    
    # 列出可用技能
    print("可用技能:")
    for skill_name in agent.skill_manager.list_skills():
        print(f"  - {skill_name}")
    
    # 使用记忆技能
    print("\n--- 使用记忆技能 ---")
    result = agent.use_skill("MemorySkill", action="store", key="user_name", value="张三")
    print(result.message)
    
    result = agent.use_skill("MemorySkill", action="recall", key="user_name")
    print(f"检索结果: {result.data}")
    
    # 使用规划技能
    print("\n--- 使用规划技能 ---")
    result = agent.use_skill("PlanningSkill", task="构建一个Web应用", steps=4)
    print(result.message)
    print(json.dumps(result.data, ensure_ascii=False, indent=2))
    
    # 组合技能
    print("\n--- 组合技能执行 ---")
    skill_chain = [
        ("WebSearchSkill", {"query": "Python best practices", "num_results": 3}),
        ("DataAnalysisSkill", {"data": [{"title": "结果1"}, {"title": "结果2"}], "analysis_type": "summary"})
    ]
    result = agent.skill_manager.compose_skills(skill_chain, agent.context)
    print(result.message)
