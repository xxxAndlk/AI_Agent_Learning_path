"""
MCP（模型上下文协议）基础实现
展示如何实现MCP Server和Client
"""

# 导入必要的标准库
# json: 用于序列化和反序列化JSON数据
# sys: 用于访问系统相关的功能（如标准输入输出）
# typing: 提供类型注解支持，增强代码可读性和IDE支持
import json
import sys
from typing import Dict, List, Any, Optional, Callable
# dataclasses: 简化数据类的创建
from dataclasses import dataclass, asdict


# ============ MCP协议消息类型定义 ============

class MCPMessage:
    """
    MCP消息基类
    所有MCP消息都继承此类，提供基本的JSON-RPC 2.0消息结构
    """
    # JSON-RPC协议版本，MCP固定使用2.0
    def __init__(self, jsonrpc: str = "2.0", id: Optional[str] = None):
        self.jsonrpc = jsonrpc
        # 请求/响应ID，用于匹配请求和响应
        self.id = id
    
    def to_dict(self) -> Dict:
        """将消息对象转换为字典格式"""
        # 返回基本的JSON-RPC结构
        return {"jsonrpc": self.jsonrpc, "id": self.id}


class InitializeRequest(MCPMessage):
    """
    初始化请求
    客户端与服务器建立连接时发送的第一个请求，用于握手协商
    """
    def __init__(self, id: str, protocol_version: str = "2024-11-05", client_info: Dict = None):
        super().__init__(id=id)  # 调用父类构造函数
        self.method = "initialize"  # 方法名，固定为initialize
        
        # 初始化参数，包含：
        # protocolVersion: 协议版本号
        # capabilities: 客户端能力声明（当前为空字典）
        # clientInfo: 客户端信息（名称和版本）
        self.params = {
            "protocolVersion": protocol_version,
            "capabilities": {},
            "clientInfo": client_info or {"name": "mcp-client", "version": "1.0.0"}
        }
    
    def to_dict(self) -> Dict:
        """将初始化请求转换为字典格式"""
        base = super().to_dict()  # 获取基类的字典表示
        base["method"] = self.method  # 添加方法名
        base["params"] = self.params  # 添加参数
        return base


class ToolsListRequest(MCPMessage):
    """
    工具列表请求
    用于获取服务器上所有可用的工具列表
    """
    def __init__(self, id: str):
        super().__init__(id=id)
        self.method = "tools/list"  # 方法名，固定为tools/list
    
    def to_dict(self) -> Dict:
        """将工具列表请求转换为字典格式"""
        base = super().to_dict()
        base["method"] = self.method
        return base


class ToolsCallRequest(MCPMessage):
    """
    工具调用请求
    用于调用服务器上的具体工具
    """
    def __init__(self, id: str, name: str, arguments: Dict):
        super().__init__(id=id)
        self.method = "tools/call"  # 方法名，固定为tools/call
        # 参数包含：
        # name: 要调用的工具名称
        # arguments: 工具执行所需的参数
        self.params = {
            "name": name,
            "arguments": arguments
        }
    
    def to_dict(self) -> Dict:
        """将工具调用请求转换为字典格式"""
        base = super().to_dict()
        base["method"] = self.method
        base["params"] = self.params
        return base


@dataclass
class MCPTool:
    """
    MCP工具定义数据类
    使用@dataclass装饰器自动生成__init__、__repr__等方法
    """
    name: str  # 工具的唯一名称
    description: str  # 工具的功能描述
    input_schema: Dict[str, Any]  # 输入参数的JSON Schema定义
    
    def to_dict(self) -> Dict:
        """将工具定义转换为字典格式"""
        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": self.input_schema
        }


class MCPServer:
    """
    MCP Server实现
    负责注册工具、处理请求、返回响应
    """
    
    def __init__(self, name: str = "mcp-server", version: str = "1.0.0"):
        """
        初始化MCP Server
        
        参数:
            name: Server名称，用于标识服务器
            version: Server版本号
        """
        self.name = name
        self.version = version
        self.tools: Dict[str, MCPTool] = {}  # 存储已注册的工具定义
        self.handlers: Dict[str, Callable] = {}  # 存储工具名称到处理函数的映射
        self.initialized = False  # 标记服务器是否已完成初始化
    
    def register_tool(self, tool: MCPTool, handler: Callable):
        """
        注册工具
        
        参数:
            tool: 工具定义对象
            handler: 工具的处理函数，当工具被调用时执行此函数
        """
        self.tools[tool.name] = tool  # 将工具添加到工具字典
        self.handlers[tool.name] = handler  # 将处理函数添加到处理器字典
        print(f"✅ 工具已注册: {tool.name}")
    
    def tool(self, name: str, description: str, schema: Dict):
        """
        装饰器方式注册工具
        
        使用示例:
        @server.tool("calculator", "计算器", {...})
        def calculator(args):
            return result
        """
        def decorator(func: Callable):
            # 创建工具定义对象
            tool = MCPTool(name=name, description=description, input_schema=schema)
            # 注册工具和处理函数
            self.register_tool(tool, func)
            return func  # 返回原函数，使其可以正常调用
        return decorator
    
    def handle_initialize(self, params: Dict) -> Dict:
        """处理初始化请求"""
        self.initialized = True  # 标记为已初始化
        # 返回服务器信息，包括协议版本、服务器信息、服务器能力
        return {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": self.name, "version": self.version},
            "capabilities": {"tools": {}}  # 声明支持tools能力
        }
    
    def handle_tools_list(self) -> Dict:
        """处理工具列表请求"""
        # 将所有已注册的工具转换为字典格式并返回
        return {
            "tools": [tool.to_dict() for tool in self.tools.values()]
        }
    
    def handle_tools_call(self, params: Dict) -> Dict:
        """处理工具调用请求"""
        tool_name = params.get("name")  # 获取要调用的工具名称
        arguments = params.get("arguments", {})  # 获取工具参数
        
        # 检查工具是否存在
        if tool_name not in self.handlers:
            return {
                "content": [{"type": "text", "text": f"未知工具: {tool_name}"}],
                "isError": True
            }
        
        try:
            # 执行工具处理函数
            result = self.handlers[tool_name](arguments)
            
            # 格式化返回结果为MCP标准格式
            if isinstance(result, str):
                # 如果结果是字符串，直接包装为text类型
                content = [{"type": "text", "text": result}]
            elif isinstance(result, dict):
                # 如果结果是字典，序列化为JSON字符串
                content = [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}]
            else:
                # 其他类型转换为字符串
                content = [{"type": "text", "text": str(result)}]
            
            return {"content": content}
        except Exception as e:
            # 捕获执行过程中的异常
            return {
                "content": [{"type": "text", "text": f"执行错误: {str(e)}"}],
                "isError": True
            }
    
    def handle_request(self, request: Dict) -> Optional[Dict]:
        """
        处理单个MCP请求
        
        参数:
            request: 包含method、params、id的请求字典
            
        返回:
            响应字典，如果不需响应则返回None
        """
        method = request.get("method")  # 获取请求方法名
        params = request.get("params", {})  # 获取请求参数
        req_id = request.get("id")  # 获取请求ID
        
        result = None
        
        # 根据方法名分发到不同的处理函数
        if method == "initialize":
            result = self.handle_initialize(params)
        elif method == "tools/list":
            result = self.handle_tools_list()
        elif method == "tools/call":
            result = self.handle_tools_call(params)
        
        # 如果有结果且请求包含ID，则返回响应
        if result is not None and req_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": result
            }
        
        return None
    
    def run_stdio(self):
        """
        以stdio模式运行Server
        从标准输入读取请求，向标准输出写入响应
        """
        print(f"🚀 MCP Server '{self.name}' 启动 (stdio模式)", file=sys.stderr)
        
        # 持续监听输入
        while True:
            try:
                # 读取一行输入
                line = sys.stdin.readline()
                if not line:  # EOF时退出
                    break
                
                line = line.strip()  # 去除首尾空白
                if not line:  # 空行跳过
                    continue
                
                # 解析JSON请求
                request = json.loads(line)
                
                # 处理请求
                response = self.handle_request(request)
                
                # 发送响应到标准输出
                if response:
                    print(json.dumps(response, ensure_ascii=False), flush=True)
                    
            except json.JSONDecodeError as e:
                # 处理JSON解析错误
                print(f"JSON解析错误: {e}", file=sys.stderr)
            except Exception as e:
                # 处理其他异常
                print(f"处理错误: {e}", file=sys.stderr)


# ============ 示例工具实现 ============

def create_sample_server():
    """
    创建示例MCP Server
    演示如何注册多个工具
    """
    # 创建服务器实例
    server = MCPServer(name="sample-server", version="1.0.0")
    
    # 定义计算器工具的参数模式（JSON Schema）
    calculator_schema = {
        "type": "object",
        "properties": {
            "a": {"type": "number", "description": "第一个数"},
            "b": {"type": "number", "description": "第二个数"},
            "operation": {
                "type": "string",
                "enum": ["add", "subtract", "multiply", "divide"],
                "description": "操作"
            }
        },
        "required": ["a", "b", "operation"]  # 必需参数
    }
    
    # 使用装饰器注册计算器工具
    @server.tool("calculator", "执行基本数学运算", calculator_schema)
    def calculator(args: Dict) -> str:
        """计算器工具的处理函数"""
        # 从参数中提取数值和操作符
        a = args.get("a", 0)
        b = args.get("b", 0)
        op = args.get("operation", "add")
        
        # 根据操作符执行相应计算
        if op == "add":
            result = a + b
        elif op == "subtract":
            result = a - b
        elif op == "multiply":
            result = a * b
        elif op == "divide":
            result = a / b if b != 0 else "除数不能为零"
        else:
            result = "未知操作"
        
        return f"结果: {result}"
    
    # 定义天气查询工具的参数模式
    weather_schema = {
        "type": "object",
        "properties": {
            "city": {"type": "string", "description": "城市名称"},
            "date": {"type": "string", "description": "日期（可选）"}
        },
        "required": ["city"]
    }
    
    # 注册天气查询工具
    @server.tool("get_weather", "查询城市天气", weather_schema)
    def get_weather(args: Dict) -> str:
        """天气查询工具的处理函数"""
        city = args.get("city", "")  # 获取城市参数
        
        # 模拟天气数据（实际应用中可调用外部API）
        weather_data = {
            "北京": "晴天，25°C，湿度45%",
            "上海": "多云，28°C，湿度60%",
            "深圳": "小雨，30°C，湿度75%",
            "广州": "阴天，29°C，湿度70%"
        }
        
        # 返回查询结果
        return weather_data.get(city, f"未找到{city}的天气信息")
    
    return server


class MCPClient:
    """
    简化版MCP Client
    负责构建请求、解析响应、管理工具列表
    """
    
    def __init__(self):
        """初始化Client"""
        self.tools: List[MCPTool] = []  # 存储已发现的工具列表
        self.request_counter = 0  # 请求计数器，用于生成唯一ID
    
    def _generate_id(self) -> str:
        """生成唯一的请求ID"""
        self.request_counter += 1
        return f"req_{self.request_counter}"
    
    def discover_tools(self, server_response: Dict) -> List[MCPTool]:
        """
        从服务器响应中解析工具列表
        
        参数:
            server_response: 包含tools列表的服务器响应
            
        返回:
            MCPTool对象列表
        """
        # 从响应中提取tools数组
        tools_data = server_response.get("result", {}).get("tools", [])
        # 将字典转换为MCPTool对象
        self.tools = [MCPTool(**tool) for tool in tools_data]
        return self.tools
    
    def call_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        构建工具调用请求
        
        参数:
            tool_name: 要调用的工具名称
            arguments: 工具参数
            
        返回:
            符合MCP协议的请求字典
        """
        return ToolsCallRequest(
            id=self._generate_id(),
            name=tool_name,
            arguments=arguments
        ).to_dict()
    
    def list_available_tools(self):
        """列出所有可用的工具"""
        print("\n可用工具:")
        for tool in self.tools:
            print(f"  - {tool.name}: {tool.description}")


# ============ 使用示例 ============

# 主程序入口
if __name__ == "__main__":
    # 创建示例服务器
    server = create_sample_server()
    
    # 创建客户端实例
    client = MCPClient()
    
    # 模拟初始化请求
    init_request = InitializeRequest(id="init_1").to_dict()
    print("初始化请求:", json.dumps(init_request, ensure_ascii=False, indent=2))
    
    # 模拟工具列表请求
    list_request = ToolsListRequest(id="list_1").to_dict()
    print("\n工具列表请求:", json.dumps(list_request, ensure_ascii=False, indent=2))
    
    # 模拟工具调用请求（调用计算器）
    call_request = ToolsCallRequest(
        id="call_1",
        name="calculator",
        arguments={"a": 10, "b": 20, "operation": "add"}
    ).to_dict()
    print("\n工具调用请求:", json.dumps(call_request, ensure_ascii=False, indent=2))
