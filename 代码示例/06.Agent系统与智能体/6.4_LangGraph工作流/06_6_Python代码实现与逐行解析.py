"""
LangGraph工作流示例
展示如何使用LangGraph构建复杂的Agent工作流
"""

# 第19行：导入类型提示相关模块
# TypedDict: 用于定义字典类型提示，提供静态类型检查支持
# Annotated: 用于添加元数据的类型提示，支持状态更新的特殊处理
# Sequence: 序列类型提示，表示有序集合（如list、tuple）
from typing import TypedDict, Annotated, Sequence
import operator

# 第22-56行：StateGraph类的定义
# 这是一个简化的StateGraph实现，用于演示LangGraph的核心原理
# 实际生产环境中建议使用langgraph库的官方实现
class StateGraph:
    """简化的StateGraph实现"""
    
    # 第26-30行：构造函数
    # 初始化工作流图的基本属性
    def __init__(self, state_type):
        self.state_type = state_type          # 状态类型（用于类型提示和验证）
        self.nodes = {}                        # 存储节点名称到函数的映射
        self.edges = {}                        # 存储普通边的映射（from -> [to]）
        self.conditional_edges = {}            # 存储条件边的映射（包含条件函数和目标映射）
    
    # 第32-34行：add_node方法
    # 用于向工作流图中添加处理节点
    def add_node(self, name, func):
        """添加节点"""
        self.nodes[name] = func                # 将节点名称和对应的处理函数存入字典
    
    # 第36-40行：add_edge方法
    # 用于添加普通边（无条件转移）
    def add_edge(self, from_node, to_node):
        """添加边"""
        if from_node not in self.edges:        # 如果起始节点尚无边记录
            self.edges[from_node] = []         # 初始化边列表
        self.edges[from_node].append(to_node)  # 将目标节点添加到边列表
    
    # 第42-44行：add_conditional_edges方法
    # 用于添加条件边（根据状态动态决定下一个节点）
    def add_conditional_edges(self, from_node, condition, conditions):
        """添加条件边"""
        # 存储条件边信息：条件函数 + 条件到目标的映射
        self.conditional_edges[from_node] = {"condition": condition, "map": conditions}
    
    # 第46-48行：set_entry_point方法
    # 设置工作流的入口节点（起始点）
    def set_entry_point(self, node):
        """设置入口节点"""
        self.entry_point = node
    
    # 第50-52行：set_finish_point方法
    # 设置工作流的结束节点（终止点）
    def set_finish_point(self, node):
        """设置结束节点"""
        self.finish_point = node
    
    # 第54-56行：compile方法
    # 将工作流图编译成可执行的CompiledGraph
    def compile(self):
        """编译工作流"""
        return CompiledGraph(self)              # 返回编译后的可执行图对象

# 第58-93行：CompiledGraph类的定义
# 编译后的图执行器，负责实际运行工作流
class CompiledGraph:
    """编译后的图"""
    
    # 第61-62行：构造函数
    # 接收StateGraph实例，保存图结构
    def __init__(self, graph):
        self.graph = graph
    
    # 第64-93行：invoke方法
    # 核心执行方法：从入口点开始遍历图直到结束点
    def invoke(self, initial_state):
        """执行工作流"""
        state = initial_state                   # 初始化状态
        current_node = self.graph.entry_point   # 从入口节点开始
        visited = set()                         # 用于检测循环
        
        # 第70-91行：主循环，持续执行直到到达结束节点
        while current_node != self.graph.finish_point:
            # 第71-73行：循环检测
            # 防止无限循环，如果节点被重复执行则抛出异常
            if current_node in visited:
                raise RuntimeError("检测到循环，但未正确处理")
            visited.add(current_node)           # 标记当前节点已访问
            
            # 第75-78行：执行当前节点
            # 获取节点对应的处理函数并执行，传入当前状态，获取更新后的状态
            func = self.graph.nodes.get(current_node)
            if func:
                state = func(state)             # 执行节点函数，更新状态
            
            # 第80-85行：处理条件边
            # 如果当前节点有条件边，根据条件函数决定下一个节点
            if current_node in self.graph.conditional_edges:
                edge_info = self.graph.conditional_edges[current_node]
                # 调用条件函数，传入当前状态，获取条件结果
                condition_result = edge_info["condition"](state)
                # 根据条件结果映射到目标节点
                current_node = edge_info["map"].get(condition_result, self.graph.finish_point)
            
            # 第86-89行：处理普通边
            # 如果当前节点有普通边，按照边的定义转移到下一个节点
            elif current_node in self.graph.edges:
                next_nodes = self.graph.edges[current_node]
                # 取第一个目标节点（简化处理）
                current_node = next_nodes[0] if next_nodes else self.graph.finish_point
            
            # 第90-91行：无法继续
            # 当前节点既没有条件边也没有普通边，退出循环
            else:
                break
        
        return state                             # 返回最终状态

# 第96-102行：AgentState状态类型定义
# 使用TypedDict定义状态的类型结构，提供IDE类型提示和静态检查
class AgentState(TypedDict):
    """Agent状态"""
    # messages: 消息历史列表，使用Annotated指定operator.add实现增量追加
    # 关键：operator.add确保新消息追加而非覆盖
    messages: Annotated[Sequence[dict], operator.add]
    next_step: str                                      # 下一步操作指示（calculate/search/chat）
    query: str                                          # 用户原始查询
    result: str                                         # 最终处理结果
    error: Optional[str]                                # 错误信息（如有）

# 第104-197行：create_agent_workflow函数
# 创建完整的Agent工作流，包含节点定义、边连接、工作流编译
def create_agent_workflow():
    """创建Agent工作流"""
    
    # 第108行：创建工作流图
    # 传入AgentState类型作为状态定义
    workflow = StateGraph(AgentState)
    
    # 第111-124行：analyze_query节点函数
    # 分析用户查询，判断应该使用哪个处理分支
    def analyze_query(state: AgentState) -> AgentState:
        """分析查询节点"""
        query = state["query"]
        
        # 第116-121行：根据查询内容判断意图类型
        if "计算" in query or "多少" in query:
            state["next_step"] = "calculate"   # 需要计算
        elif "搜索" in query or "查询" in query:
            state["next_step"] = "search"      # 需要搜索
        else:
            state["next_step"] = "chat"        # 通用对话
        
        # 第123行：记录分析结果到消息历史
        state["messages"].append({"role": "system", "content": f"分析结果: 使用{state['next_step']}处理"})
        return state
    
    # 第126-144行：calculate节点函数
    # 处理数学计算请求
    def calculate(state: AgentState) -> AgentState:
        """计算节点"""
        query = state["query"]
        
        try:
            # 第133行：使用正则表达式提取查询中的数字
            import re
            numbers = re.findall(r'\d+', query)
            
            # 第134-138行：执行加法计算
            if len(numbers) >= 2:
                result = int(numbers[0]) + int(numbers[1])
                state["result"] = f"计算结果: {result}"
            else:
                state["result"] = "无法提取有效数字"
        
        # 第139-141行：异常处理
        except Exception as e:
            state["error"] = str(e)
            state["result"] = "计算失败"
        
        # 第143行：记录计算结果到消息历史
        state["messages"].append({"role": "assistant", "content": state["result"]})
        return state
    
    # 第146-152行：search节点函数
    # 处理搜索请求（模拟实现）
    def search(state: AgentState) -> AgentState:
        """搜索节点"""
        query = state["query"]
        
        # 第150行：生成模拟搜索结果
        state["result"] = f"搜索结果: 找到关于'{query}'的10条相关信息"
        state["messages"].append({"role": "assistant", "content": state["result"]})
        return state
    
    # 第154-160行：chat节点函数
    # 处理通用对话请求（模拟实现）
    def chat(state: AgentState) -> AgentState:
        """对话节点"""
        query = state["query"]
        
        # 第158行：生成模拟对话回复
        state["result"] = f"这是关于'{query}'的回答"
        state["messages"].append({"role": "assistant", "content": state["result"]})
        return state
    
    # 第162-168行：should_continue函数
    # 判断工作流是否应该继续执行（用于更复杂的条件判断场景）
    def should_continue(state: AgentState) -> str:
        """判断是否应该继续"""
        if state.get("error"):
            return "error"          # 有错误，转到错误处理
        if state.get("result"):
            return "end"            # 有结果，结束工作流
        return "continue"           # 继续执行
    
    # 第171-174行：向工作流添加节点
    # 将前面定义的各节点函数注册到工作流中
    workflow.add_node("analyze", analyze_query)
    workflow.add_node("calculate", calculate)
    workflow.add_node("search", search)
    workflow.add_node("chat", chat)
    
    # 第177行：设置工作流入口点
    # 设置analyze作为工作流的起始节点
    workflow.set_entry_point("analyze")
    
    # 第180-188行：添加条件边
    # 根据analyze节点的判断结果（next_step），决定后续走哪个分支
    workflow.add_conditional_edges(
        "analyze",                           # 起始节点
        lambda s: s["next_step"],            # 条件函数：从状态中获取next_step
        {                                    # 条件到目标节点的映射
            "calculate": "calculate",
            "search": "search",
            "chat": "chat"
        }
    )
    
    # 第191-192行：添加结束边
    # 所有处理节点执行完后，转向结束节点
    for node in ["calculate", "search", "chat"]:
        workflow.add_edge(node, "__end__")   # 连接到结束节点
    
    # 第194行：设置工作流结束点
    workflow.set_finish_point("__end__")
    
    # 第197行：编译工作流
    # 将图结构编译成可执行的CompiledGraph对象
    return workflow.compile()

# 第200-216行：使用示例
# 演示如何创建和执行工作流
if __name__ == "__main__":
    # 第202行：创建编译后的工作流
    app = create_agent_workflow()
    
    # 第205-211行：构建初始状态
    # 定义工作流的初始输入数据
    initial_state = {
        "messages": [],                      # 初始空消息列表
        "next_step": "",                     # 初始无下一步指示
        "query": "计算3加5等于多少",         # 用户查询（会触发calculate分支）
        "result": "",                        # 初始结果为空
        "error": None                        # 初始无错误
    }
    
    # 第213行：执行工作流
    # 调用invoke方法，开始遍历图并执行各节点
    final_state = app.invoke(initial_state)
    
    # 第214-215行：输出结果
    print("最终结果:", final_state["result"])
    print("消息历史:", final_state["messages"])
