"""
Multi-Agent架构实现
展示不同Multi-Agent架构模式的实现
"""

from typing import Dict, List, Any, Optional, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import asyncio

class ArchitectureType(Enum):
    """Multi-Agent架构类型"""
    MASTER_SLAVE = "master_slave"       # 主从架构
    PEER_TO_PEER = "peer_to_peer"       # 对等架构
    HIERARCHICAL = "hierarchical"       # 层级架构
    FEDERATED = "federated"             # 联邦架构


@dataclass
class AgentCapability:
    """Agent能力定义"""
    name: str              # 能力名称
    description: str      # 能力描述
    input_types: List[str]  # 输入类型
    output_types: List[str]  # 输出类型
    performance_score: float = 1.0  # 性能评分


class BaseAgent(ABC):
    """Multi-Agent系统中的基础Agent类
    
    所有具体Agent都需要继承此类并实现抽象方法
    """
    
    def __init__(self, agent_id: str, name: str):
        """
        初始化基础Agent
        
        参数:
            agent_id: Agent唯一标识
            name: Agent名称
        """
        self.agent_id = agent_id  # 设置Agent ID
        self.name = name  # 设置Agent名称
        self.capabilities: List[AgentCapability] = []  # 能力列表，初始化为空
        self.status: str = "idle"  # Agent状态：idle/busy/offline
        self.message_queue: asyncio.Queue = asyncio.Queue()  # 消息队列，用于接收消息
        self.neighbors: List[str] = []  # 相邻Agent列表，用于P2P架构
        self.parent: Optional[str] = None  # 父Agent ID，用于层级架构
        self.children: List[str] = []  # 子Agent ID列表，用于层级架构
    
    def add_capability(self, capability: AgentCapability):
        """
        添加能力
        
        参数:
            capability: Agent能力对象
        """
        self.capabilities.append(capability)  # 将能力添加到能力列表
    
    @abstractmethod
    async def process_task(self, task: Dict) -> Any:
        """
        处理任务（子类必须实现）
        
        参数:
            task: 任务字典
        返回:
            任务处理结果
        """
        pass
    
    @abstractmethod
    async def handle_message(self, message: Dict) -> Optional[Dict]:
        """
        处理消息（子类必须实现）
        
        参数:
            message: 消息字典
        返回:
            响应消息（如果有）
        """
        pass


class MasterSlaveArchitecture:
    """主从架构实现
    
    特点：
    - 一个Master Agent协调多个Slave Agent
    - Master负责任务分配和结果汇总
    - Slave负责具体任务执行
    """
    
    def __init__(self):
        """初始化主从架构"""
        self.master: Optional[BaseAgent] = None  # Master Agent
        self.slaves: Dict[str, BaseAgent] = {}  # Slave Agent字典
        self.task_queue: asyncio.Queue = asyncio.Queue()  # 任务队列
    
    def set_master(self, master: BaseAgent):
        """设置Master Agent"""
        self.master = master
    
    def add_slave(self, slave: BaseAgent):
        """添加Slave Agent"""
        self.slaves[slave.agent_id] = slave  # 将Slave添加到字典
    
    async def distribute_task(self, task: Dict) -> Dict[str, Any]:
        """
        分发任务给Slave执行
        
        参数:
            task: 要执行的任务
        返回:
            执行结果字典
        """
        results = {}
        
        # 根据任务类型选择Slave
        task_type = task.get("type", "default")  # 获取任务类型
        # 筛选具有相应能力的Slave
        capable_slaves = [
            slave for slave in self.slaves.values()
            if any(cap.name == task_type for cap in slave.capabilities)
        ]
        
        if not capable_slaves:
            raise ValueError(f"没有Agent能处理任务类型: {task_type}")
        
        # 选择负载最低的Slave
        selected_slave = min(capable_slaves, key=lambda s: s.status == "busy")
        selected_slave.status = "busy"  # 标记为忙碌
        
        try:
            # 执行任务
            result = await selected_slave.process_task(task)
            results[selected_slave.agent_id] = result  # 记录结果
        finally:
            selected_slave.status = "idle"  # 执行完成后重置状态
        
        return results
    
    async def broadcast_task(self, task: Dict) -> Dict[str, Any]:
        """
        广播任务给所有Slave并行执行
        
        参数:
            task: 要执行的任务
        返回:
            所有Slave的执行结果
        """
        tasks = []
        for slave in self.slaves.values():
            if slave.status == "idle":
                slave.status = "busy"  # 标记为忙碌
                # 创建异步任务并行执行
                t = asyncio.create_task(self._execute_and_release(slave, task))
                tasks.append(t)
        
        # 等待所有任务完成
        results_list = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = {}
        for slave_id, result in zip(self.slaves.keys(), results_list):
            if not isinstance(result, Exception):
                results[slave_id] = result
        
        return results
    
    async def _execute_and_release(self, slave: BaseAgent, task: Dict):
        """执行任务并释放Slave"""
        try:
            return await slave.process_task(task)
        finally:
            slave.status = "idle"  # 释放Slave


class PeerToPeerArchitecture:
    """对等架构实现
    
    特点：
    - 所有Agent地位平等
    - Agent之间直接通信
    - 支持任务委托和协作
    """
    
    def __init__(self):
        """初始化对等架构"""
        self.agents: Dict[str, BaseAgent] = {}  # Agent字典
        self.message_router: Dict[str, Callable] = {}  # 消息路由器
    
    def add_agent(self, agent: BaseAgent):
        """添加Agent到网络"""
        self.agents[agent.agent_id] = agent  # 添加到Agent字典
        
        # 建立邻居关系（简化实现：所有Agent互相连接）
        for other_agent in self.agents.values():
            if other_agent.agent_id != agent.agent_id:
                agent.neighbors.append(other_agent.agent_id)
                other_agent.neighbors.append(agent.agent_id)
    
    async def send_message(self, from_id: str, to_id: str, message: Dict):
        """发送点对点消息"""
        if to_id not in self.agents:
            raise ValueError(f"目标Agent不存在: {to_id}")
        
        # 添加路由信息到消息
        message["from"] = from_id
        message["to"] = to_id
        message["timestamp"] = datetime.now().isoformat()
        
        # 将消息放入目标Agent的队列
        await self.agents[to_id].message_queue.put(message)
    
    async def broadcast(self, from_id: str, message: Dict):
        """广播消息给所有Agent"""
        for agent_id in self.agents:
            if agent_id != from_id:
                await self.send_message(from_id, agent_id, message)
    
    async def delegate_task(self, from_id: str, to_id: str, task: Dict) -> Any:
        """委托任务给其他Agent"""
        if to_id not in self.agents:
            raise ValueError(f"目标Agent不存在: {to_id}")
        
        agent = self.agents[to_id]
        agent.status = "busy"  # 标记为忙碌
        
        try:
            # 执行任务
            result = await agent.process_task(task)
            return result
        finally:
            agent.status = "idle"  # 释放Agent
    
    async def find_agent_with_capability(self, capability_name: str) -> Optional[str]:
        """查找具有特定能力的Agent"""
        for agent_id, agent in self.agents.items():
            # 检查是否有匹配的能力且状态空闲
            if any(cap.name == capability_name for cap in agent.capabilities):
                if agent.status == "idle":
                    return agent_id
        return None


class HierarchicalArchitecture:
    """层级架构实现
    
    特点：
    - Agent组织成树形结构
    - 父Agent管理子Agent
    - 任务逐级分解和汇总
    """
    
    def __init__(self):
        """初始化层级架构"""
        self.agents: Dict[str, BaseAgent] = {}  # Agent字典
        self.root: Optional[str] = None  # 根节点
    
    def add_agent(self, agent: BaseAgent, parent_id: Optional[str] = None):
        """添加Agent到层级结构"""
        self.agents[agent.agent_id] = agent
        
        if parent_id:
            if parent_id not in self.agents:
                raise ValueError(f"父Agent不存在: {parent_id}")
            
            # 设置父子关系
            agent.parent = parent_id
            self.agents[parent_id].children.append(agent.agent_id)
        else:
            # 没有父节点，设为根
            self.root = agent.agent_id
    
    async def cascade_task(self, agent_id: str, task: Dict) -> Dict[str, Any]:
        """级联任务到子Agent"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent不存在: {agent_id}")
        
        agent = self.agents[agent_id]
        # 处理当前节点的任务
        results = {agent_id: await agent.process_task(task)}
        
        # 递归分发给子Agent
        for child_id in agent.children:
            child_results = await self.cascade_task(child_id, task)
            results.update(child_results)
        
        return results
    
    async def aggregate_results(self, agent_id: str) -> Dict[str, Any]:
        """从子Agent聚合结果"""
        if agent_id not in self.agents:
            raise ValueError(f"Agent不存在: {agent_id}")
        
        agent = self.agents[agent_id]
        aggregated = {"agent_id": agent_id, "children_results": []}
        
        # 递归聚合子结果
        for child_id in agent.children:
            child_result = await self.aggregate_results(child_id)
            aggregated["children_results"].append(child_result)
        
        return aggregated
    
    def get_tree_structure(self) -> Dict:
        """获取树形结构"""
        if not self.root:
            return {}
        
        def build_tree(agent_id: str) -> Dict:
            agent = self.agents[agent_id]
            return {
                "agent_id": agent_id,
                "name": agent.name,
                "capabilities": [cap.name for cap in agent.capabilities],
                "children": [build_tree(child_id) for child_id in agent.children]
            }
        
        return build_tree(self.root)


# 使用示例
if __name__ == "__main__":
    # 创建具体的Agent实现
    class SimpleAgent(BaseAgent):
        async def process_task(self, task: Dict) -> Any:
            await asyncio.sleep(0.1)  # 模拟处理时间
            return f"Agent {self.name} 处理任务: {task.get('name', 'unknown')}"
        
        async def handle_message(self, message: Dict) -> Optional[Dict]:
            return {"ack": True, "from": self.agent_id}
    
    # 测试主从架构
    print("=== 主从架构测试 ===")
    master_slave = MasterSlaveArchitecture()
    master = SimpleAgent("master_1", "Master")
    slave1 = SimpleAgent("slave_1", "Worker-1")
    slave2 = SimpleAgent("slave_2", "Worker-2")
    
    master_slave.set_master(master)
    master_slave.add_slave(slave1)
    master_slave.add_slave(slave2)
    
    # 运行测试
    async def test_master_slave():
        task = {"type": "compute", "name": "数据分析任务"}
        results = await master_slave.distribute_task(task)
        print(f"任务分配结果: {results}")
    
    asyncio.run(test_master_slave())
