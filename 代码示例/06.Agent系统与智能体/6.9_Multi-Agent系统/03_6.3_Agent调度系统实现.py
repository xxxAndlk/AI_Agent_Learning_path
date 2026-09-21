"""
Agent调度系统
实现多Agent环境下的任务调度策略
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import heapq
import asyncio

class SchedulingStrategy(Enum):
    """调度策略"""
    ROUND_ROBIN = "round_robin"         # 轮询
    LEAST_LOADED = "least_loaded"       # 最小负载
    PRIORITY_BASED = "priority"         # 优先级
    CAPABILITY_MATCH = "capability"     # 能力匹配
    COST_OPTIMIZED = "cost"             # 成本优化


@dataclass
class AgentResource:
    """Agent资源信息"""
    cpu_percent: float = 0.0            # CPU使用率
    memory_percent: float = 0.0         # 内存使用率
    active_tasks: int = 0               # 活跃任务数
    queue_depth: int = 0                # 队列深度
    last_heartbeat: Optional[datetime] = None
    is_online: bool = True


@dataclass
class Task:
    """任务定义"""
    task_id: str  # 任务ID
    task_type: str  # 任务类型
    priority: int  # 优先级 1-5，5最高
    required_capabilities: List[str]  # 所需能力
    estimated_duration: timedelta  # 预估时长
    deadline: Optional[datetime]  # 截止时间
    payload: Dict[str, Any]  # 任务数据
    created_at: datetime  # 创建时间


class AgentScheduler:
    """Agent调度器"""
    
    def __init__(self, strategy: SchedulingStrategy = SchedulingStrategy.LEAST_LOADED):
        """
        初始化调度器
        
        参数:
            strategy: 调度策略
        """
        self.strategy = strategy  # 设置调度策略
        self.agents: Dict[str, Dict] = {}  # Agent信息
        self.task_queue: List[tuple] = []  # 任务队列（优先级队列）
        self.task_counter = 0  # 任务计数器
    
    def register_agent(
        self,
        agent_id: str,
        capabilities: List[str],
        capacity: int = 5
    ):
        """
        注册Agent
        
        参数:
            agent_id: Agent唯一标识
            capabilities: Agent能力列表
            capacity: 最大并发任务数
        """
        self.agents[agent_id] = {
            "capabilities": set(capabilities),  # 能力集合
            "capacity": capacity,  # 容量
            "resources": AgentResource(),  # 资源信息
            "assigned_tasks": []  # 已分配任务
        }
    
    def update_agent_resources(self, agent_id: str, resources: AgentResource):
        """更新Agent资源状态"""
        if agent_id in self.agents:
            self.agents[agent_id]["resources"] = resources
    
    def submit_task(self, task: Task) -> bool:
        """
        提交任务到调度队列
        
        参数:
            task: 任务对象
        返回:
            是否成功提交
        """
        # 使用优先级队列（优先级越高，数值越小）
        # 格式: (优先级, 计数器, 任务)
        priority_value = 10 - task.priority  # 反转优先级，使高优先级排前面
        heapq.heappush(self.task_queue, (priority_value, self.task_counter, task))
        self.task_counter += 1
        return True
    
    def schedule_task(self) -> Optional[tuple]:
        """
        调度一个任务
        
        返回:
            (task_id, agent_id) 或 None
        """
        if not self.task_queue:
            return None  # 队列为空
        
        # 获取最高优先级任务
        _, _, task = heapq.heappop(self.task_queue)
        
        # 选择合适的Agent
        selected_agent = self._select_agent_for_task(task)
        
        if selected_agent:
            # 分配任务
            self.agents[selected_agent]["assigned_tasks"].append(task.task_id)
            return (task.task_id, selected_agent)
        else:
            # 没有可用Agent，任务放回队列
            heapq.heappush(self.task_queue, (10 - task.priority, self.task_counter, task))
            self.task_counter += 1
            return None
    
    def _select_agent_for_task(self, task: Task) -> Optional[str]:
        """为任务选择最合适的Agent"""
        candidates = []
        
        for agent_id, agent_info in self.agents.items():
            # 检查Agent是否在线
            if not agent_info["resources"].is_online:
                continue
            
            # 检查能力匹配
            if not all(cap in agent_info["capabilities"] for cap in task.required_capabilities):
                continue
            
            # 检查容量
            if len(agent_info["assigned_tasks"]) >= agent_info["capacity"]:
                continue
            
            # 根据策略计算得分
            score = self._calculate_agent_score(agent_id, agent_info, task)
            candidates.append((score, agent_id))
        
        if not candidates:
            return None
        
        # 选择得分最高的Agent
        best_agent = max(candidates, key=lambda x: x[0])
        return best_agent[1]
    
    def _calculate_agent_score(self, agent_id: str, agent_info: Dict, task: Task) -> float:
        """计算Agent得分（越高越好）"""
        resources = agent_info["resources"]
        
        if self.strategy == SchedulingStrategy.LEAST_LOADED:
            # 最小负载优先
            load_factor = (
                resources.cpu_percent * 0.4 +
                resources.memory_percent * 0.3 +
                (len(agent_info["assigned_tasks"]) / agent_info["capacity"]) * 0.3
            )
            return 100 - load_factor
        
        elif self.strategy == SchedulingStrategy.CAPABILITY_MATCH:
            # 能力匹配度
            matching_caps = len(
                set(agent_info["capabilities"]) & set(task.required_capabilities)
            )
            return matching_caps / len(task.required_capabilities) * 100
        
        elif self.strategy == SchedulingStrategy.ROUND_ROBIN:
            # 轮询（简化实现：选择任务最少的）
            return 100 - len(agent_info["assigned_tasks"]) * 10
        
        else:
            # 默认策略
            return 50.0
    
    def get_schedule_status(self) -> Dict:
        """获取调度状态"""
        return {
            "queued_tasks": len(self.task_queue),
            "registered_agents": len(self.agents),
            "strategy": self.strategy.value,
            "agent_loads": {
                agent_id: len(info["assigned_tasks"])
                for agent_id, info in self.agents.items()
            }
        }
    
    def complete_task(self, agent_id: str, task_id: str):
        """标记任务完成"""
        if agent_id in self.agents:
            if task_id in self.agents[agent_id]["assigned_tasks"]:
                self.agents[agent_id]["assigned_tasks"].remove(task_id)


class DynamicScheduler:
    """动态调度器
    
    支持任务抢占、动态资源调整
    """
    
    def __init__(self):
        """初始化动态调度器"""
        self.scheduler = AgentScheduler()  # 基础调度器
        self.running_tasks: Dict[str, Dict] = {}  # 正在执行的任务
        self.preemption_enabled = True  # 抢占使能
    
    def preempt_task(self, low_priority_task_id: str, high_priority_task: Task) -> bool:
        """
        抢占低优先级任务
        
        参数:
            low_priority_task_id: 被抢占的任务ID
            high_priority_task: 高优先级任务
        返回:
            是否成功抢占
        """
        if not self.preemption_enabled:
            return False  # 抢占未使能
        
        if low_priority_task_id not in self.running_tasks:
            return False  # 任务不在运行
        
        task_info = self.running_tasks[low_priority_task_id]
        
        # 检查是否可以抢占（优先级差>=2）
        if high_priority_task.priority - task_info["priority"] < 2:
            return False  # 优先级差不够
        
        # 执行抢占
        agent_id = task_info["agent_id"]
        self.scheduler.complete_task(agent_id, low_priority_task_id)
        del self.running_tasks[low_priority_task_id]
        
        # 将抢占的任务放回队列
        self.scheduler.submit_task(high_priority_task)
        
        return True  # 抢占成功
    
    def auto_scale(self):
        """自动扩缩容（简化实现）"""
        status = self.scheduler.get_schedule_status()
        
        # 如果队列任务过多，可以考虑增加Agent
        if status["queued_tasks"] > 20:
            print("建议：队列任务过多，考虑增加Agent")
        
        # 如果所有Agent都空闲，可以考虑减少Agent
        all_idle = all(load == 0 for load in status["agent_loads"].values())
        if all_idle and len(status["agent_loads"]) > 2:
            print("建议：Agent空闲率过高，考虑减少Agent")


# 使用示例
if __name__ == "__main__":
    # 创建调度器
    scheduler = AgentScheduler(strategy=SchedulingStrategy.LEAST_LOADED)
    
    # 注册Agent
    scheduler.register_agent("agent_1", ["compute", "analyze"], capacity=3)
    scheduler.register_agent("agent_2", ["compute", "transform"], capacity=5)
    scheduler.register_agent("agent_3", ["analyze", "report"], capacity=2)
    
    # 模拟资源更新
    scheduler.update_agent_resources("agent_1", AgentResource(
        cpu_percent=30.0,
        memory_percent=40.0,
        active_tasks=1,
        is_online=True,
        last_heartbeat=datetime.now()
    ))
    
    # 提交任务
    tasks = [
        Task(
            task_id=f"task_{i}",
            task_type="compute",
            priority=3,
            required_capabilities=["compute"],
            estimated_duration=timedelta(minutes=5),
            deadline=None,
            payload={"data": f"data_{i}"},
            created_at=datetime.now()
        )
        for i in range(5)
    ]
    
    for task in tasks:
        scheduler.submit_task(task)
    
    print("=== 调度前状态 ===")
    print(scheduler.get_schedule_status())
    
    # 调度任务
    print("\n=== 任务调度 ===")
    for _ in range(5):
        result = scheduler.schedule_task()
        if result:
            print(f"任务 {result[0]} 分配给 Agent {result[1]}")
        else:
            print("无可用Agent，任务留在队列")
    
    print("\n=== 调度后状态 ===")
    print(scheduler.get_schedule_status())
