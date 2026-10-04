"""
Agent Trace系统
追踪Agent执行链路和状态变化
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

class TraceEventType(Enum):
    """Trace事件类型"""
    AGENT_START = "agent_start"
    THOUGHT = "thought"
    ACTION = "action"
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    OBSERVATION = "observation"
    ERROR = "error"
    AGENT_END = "agent_end"

@dataclass
class TraceEvent:
    """Trace事件"""
    event_id: str
    timestamp: datetime
    event_type: TraceEventType
    agent_id: str
    content: Dict[str, Any]
    duration_ms: Optional[float] = None
    parent_id: Optional[str] = None

@dataclass
class AgentTrace:
    """Agent追踪记录"""
    trace_id: str
    agent_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    events: List[TraceEvent] = field(default_factory=list)
    status: str = "running"  # running/completed/failed
    metadata: Dict = field(default_factory=dict)

class AgentTracer:
    """Agent追踪器"""
    
    def __init__(self):
        self.active_traces: Dict[str, AgentTrace] = {}
        self.completed_traces: List[AgentTrace] = []
        self.event_counter = 0
    
    def start_trace(self, agent_id: str, metadata: Optional[Dict] = None) -> str:
        """开始追踪"""
        trace_id = f"trace_{datetime.now().timestamp()}"
        trace = AgentTrace(
            trace_id=trace_id,
            agent_id=agent_id,
            start_time=datetime.now(),
            metadata=metadata or {}
        )
        self.active_traces[trace_id] = trace
        
        # 记录开始事件
        self._add_event(trace_id, TraceEventType.AGENT_START, {
            "message": f"Agent {agent_id} started"
        })
        
        return trace_id
    
    def _add_event(
        self,
        trace_id: str,
        event_type: TraceEventType,
        content: Dict,
        duration_ms: Optional[float] = None
    ):
        """添加事件"""
        if trace_id not in self.active_traces:
            return
        
        self.event_counter += 1
        event = TraceEvent(
            event_id=f"evt_{self.event_counter}",
            timestamp=datetime.now(),
            event_type=event_type,
            agent_id=self.active_traces[trace_id].agent_id,
            content=content,
            duration_ms=duration_ms
        )
        
        self.active_traces[trace_id].events.append(event)
    
    def log_thought(self, trace_id: str, thought: str):
        """记录思考过程"""
        self._add_event(trace_id, TraceEventType.THOUGHT, {"thought": thought})
    
    def log_action(self, trace_id: str, action: str, params: Dict):
        """记录行动"""
        self._add_event(trace_id, TraceEventType.ACTION, {
            "action": action,
            "params": params
        })
    
    def log_tool_call(self, trace_id: str, tool_name: str, params: Dict):
        """记录工具调用"""
        self._add_event(trace_id, TraceEventType.TOOL_CALL, {
            "tool": tool_name,
            "params": params
        })
    
    def log_tool_result(self, trace_id: str, tool_name: str, result: Any, duration_ms: float):
        """记录工具结果"""
        self._add_event(trace_id, TraceEventType.TOOL_RESULT, {
            "tool": tool_name,
            "result": result
        }, duration_ms=duration_ms)
    
    def end_trace(self, trace_id: str, status: str = "completed"):
        """结束追踪"""
        if trace_id not in self.active_traces:
            return
        
        trace = self.active_traces[trace_id]
        trace.end_time = datetime.now()
        trace.status = status
        
        # 记录结束事件
        self._add_event(trace_id, TraceEventType.AGENT_END, {
            "status": status,
            "total_events": len(trace.events)
        })
        
        # 移到完成列表
        self.completed_traces.append(trace)
        del self.active_traces[trace_id]
    
    def get_trace(self, trace_id: str) -> Optional[AgentTrace]:
        """获取Trace"""
        if trace_id in self.active_traces:
            return self.active_traces[trace_id]
        return next((t for t in self.completed_traces if t.trace_id == trace_id), None)
    
    def export_trace(self, trace_id: str) -> str:
        """导出Trace为JSON"""
        trace = self.get_trace(trace_id)
        if not trace:
            return "{}"
        
        return json.dumps({
            "trace_id": trace.trace_id,
            "agent_id": trace.agent_id,
            "start_time": trace.start_time.isoformat(),
            "end_time": trace.end_time.isoformat() if trace.end_time else None,
            "status": trace.status,
            "events": [
                {
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "type": e.event_type.value,
                    "content": e.content,
                    "duration_ms": e.duration_ms
                }
                for e in trace.events
            ]
        }, indent=2, default=str)


# 使用示例
if __name__ == "__main__":
    tracer = AgentTracer()
    
    # 开始追踪
    trace_id = tracer.start_trace("agent_001", {"task": "data_analysis"})
    
    # 模拟Agent执行
    tracer.log_thought(trace_id, "我需要分析这个数据")
    tracer.log_action(trace_id, "load_data", {"file": "data.csv"})
    tracer.log_tool_call(trace_id, "csv_reader", {"path": "data.csv"})
    tracer.log_tool_result(trace_id, "csv_reader", {"rows": 1000}, 50.0)
    tracer.log_thought(trace_id, "数据加载完成，开始分析")
    
    # 结束追踪
    tracer.end_trace(trace_id, "completed")
    
    # 导出Trace
    print("Agent Trace:")
    print(tracer.export_trace(trace_id))
