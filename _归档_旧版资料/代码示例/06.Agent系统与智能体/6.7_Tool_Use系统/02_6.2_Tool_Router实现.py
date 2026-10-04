"""
Tool Router实现
展示如何根据用户意图智能选择工具
"""

# 导入所需模块
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import re  # 正则表达式模块
import json  # JSON处理

@dataclass
class RoutingResult:
    """路由结果数据类 - 封装路由决策的结果"""
    tool_name: str                     # 选中的工具名称
    confidence: float                  # 置信度（0-1之间）
    arguments: Dict[str, Any]          # 提取的参数
    alternative_tools: List[str]       # 备选工具列表


class ToolRouter:
    """工具路由器类
    
    功能：
    1. 意图识别：分析用户输入确定意图
    2. 工具匹配：将意图映射到工具
    3. 参数提取：从输入中提取工具参数
    """
    
    def __init__(self):
        """初始化路由器"""
        self.tools: Dict[str, Dict] = {}          # 注册的工具字典
        self.intent_patterns: Dict[str, List] = {}  # 意图匹配模式字典
    
    def register_tool(self, schema: ToolSchema, keywords: List[str]):
        """
        注册工具到路由器
        
        参数:
            schema: 工具Schema - 工具的定义
            keywords: 意图关键词列表 - 用于匹配用户意图
        """
        # 将工具信息存入字典
        self.tools[schema.name] = {
            "schema": schema,
            "keywords": keywords
        }
        
        # 编译正则表达式模式以提高匹配效率
        # re.escape转义特殊字符，re.IGNORECASE忽略大小写
        self.intent_patterns[schema.name] = [
            re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
            for kw in keywords
        ]
    
    def route(self, user_input: str, context: Dict = None) -> RoutingResult:
        """
        路由用户请求到合适的工具
        
        参数:
            user_input: 用户输入 - 需要进行路由的文本
            context: 上下文信息（可选）- 用于辅助决策的额外信息
        返回:
            RoutingResult - 包含选中工具、置信度和参数的路由结果
        """
        # 1. 意图识别 - 计算每个工具的匹配分数
        scores = self._calculate_intent_scores(user_input)
        
        # 如果没有匹配的工具，返回空结果
        if not scores:
            return RoutingResult(
                tool_name="",
                confidence=0.0,
                arguments={},
                alternative_tools=[]
            )
        
        # 2. 选择最佳匹配 - 找到分数最高的工具
        best_tool = max(scores.items(), key=lambda x: x[1])
        tool_name = best_tool[0]
        confidence = best_tool[1]
        
        # 3. 参数提取 - 从用户输入中提取参数
        tool_info = self.tools[tool_name]
        arguments = self._extract_arguments(user_input, tool_info["schema"])
        
        # 4. 获取备选工具 - 分数>0.3的其他工具
        alternatives = [
            name for name, score in scores.items()
            if name != tool_name and score > 0.3
        ]
        
        return RoutingResult(
            tool_name=tool_name,
            confidence=confidence,
            arguments=arguments,
            alternative_tools=alternatives[:3]  # 最多返回3个备选
        )
    
    def _calculate_intent_scores(self, user_input: str) -> Dict[str, float]:
        """
        计算意图匹配分数
        使用关键词匹配和密度计算来评估每个工具的相关性
        """
        scores = {}
        
        # 遍历所有已注册的工具和它们的模式
        for tool_name, patterns in self.intent_patterns.items():
            score = 0.0
            # 统计关键词匹配次数
            for pattern in patterns:
                matches = len(pattern.findall(user_input))
                score += matches * 0.3  # 每个匹配加0.3分
            
            # 计算关键词密度（匹配词占总词数比例）
            words = user_input.split()
            if words:
                # 统计有多少个模式在输入中找到
                keyword_count = sum(1 for p in patterns if p.search(user_input))
                # 密度分数：匹配的模式数 / 总模式数，加权0.4
                score += (keyword_count / len(patterns)) * 0.4
            
            # 只保留分数>0的工具，最高分为1.0
            if score > 0:
                scores[tool_name] = min(score, 1.0)
        
        return scores
    
    def _extract_arguments(self, user_input: str, schema: ToolSchema) -> Dict[str, Any]:
        """
        从用户输入提取参数
        针对不同参数类型使用不同的提取策略
        """
        arguments = {}
        
        # 遍历schema中的参数定义
        for param in schema.parameters:
            # 城市名提取策略
            if param.name == "city":
                # 使用正则提取中文城市名（2-10个汉字）
                city_match = re.search(r'([\u4e00-\u9fa5]{2,10}市?)', user_input)
                if city_match:
                    # 去掉"市"字
                    arguments[param.name] = city_match.group(1).replace("市", "")
            
            # 数学表达式提取策略
            elif param.name == "expression":
                # 提取数字和运算符组成的表达式
                expr_match = re.search(r'([\d\s\+\-\*\/\(\)\.]+)', user_input)
                if expr_match:
                    arguments[param.name] = expr_match.group(1).strip()
            
            # 搜索查询提取策略
            elif param.name == "query":
                # 提取引号内或特定格式的查询内容
                query_match = re.search(r'搜索["\']?(.+?)["\']?(?:的结果|相关信息)?', user_input)
                if query_match:
                    arguments[param.name] = query_match.group(1)
        
        return arguments


class LLMBasedRouter:
    """基于LLM的智能路由器类
    
    使用大语言模型进行更智能的路由决策
    适用于复杂意图或关键词匹配不准确场景
    """
    
    def __init__(self, llm_client):
        """
        初始化LLM路由器
        
        参数:
            llm_client: LLM客户端 - 支持chat接口的对象（如OpenAI）
        """
        self.llm = llm_client
        self.tools: Dict[str, ToolSchema] = {}
    
    def register_tool(self, schema: ToolSchema):
        """注册工具"""
        self.tools[schema.name] = schema
    
    def route_with_llm(self, user_input: str) -> RoutingResult:
        """
        使用LLM进行智能路由
        
        参数:
            user_input: 用户输入
        返回:
            RoutingResult - LLM返回的路由决策结果
        """
        # 构建工具描述文本
        tools_desc = "\n".join([
            f"- {name}: {schema.description}"
            for name, schema in self.tools.items()
        ])
        
        # 构造提示词，引导LLM返回结构化结果
        prompt = f"""分析用户的意图，选择最合适的工具。

可用工具：
{tools_desc}

用户输入：{user_input}

请以JSON格式返回：
{{
    "tool_name": "选中的工具名称",
    "confidence": 0.95,
    "arguments": {{"参数名": "参数值"}},
    "reasoning": "选择理由"
}}"""
        
        try:
            # 调用LLM的chat接口
            response = self.llm.chat.completions.create(
                model="gpt-5.4-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            # 解析LLM返回的JSON结果
            result = json.loads(response.choices[0].message.content)
            
            return RoutingResult(
                tool_name=result.get("tool_name", ""),
                confidence=result.get("confidence", 0.0),
                arguments=result.get("arguments", {}),
                alternative_tools=[]
            )
        except Exception as e:
            print(f"LLM路由失败: {e}")
            return RoutingResult("", 0.0, {}, [])


# 使用示例
if __name__ == "__main__":
    # 导入schema创建函数（实际使用时应从其他模块导入）
    from ai应用开发学习文档 import create_calculator_schema, create_weather_schema, create_search_schema
    
    # 创建路由器实例
    router = ToolRouter()
    
    # 注册工具及其关键词
    router.register_tool(
        create_calculator_schema(),
        keywords=["计算", "等于", "结果是", "+", "-", "*", "/", "加", "减", "乘", "除"]
    )
    router.register_tool(
        create_weather_schema(),
        keywords=["天气", "温度", "下雨", "晴天", "湿度", "气温"]
    )
    router.register_tool(
        create_search_schema(),
        keywords=["搜索", "查找", "查询", "关于", "信息"]
    )
    
    # 测试路由功能
    test_inputs = [
        "北京今天天气怎么样？",
        "计算 15 + 25 等于多少",
        "帮我搜索关于人工智能的信息"
    ]
    
    print("=== Tool Router 测试 ===\n")
    for user_input in test_inputs:
        result = router.route(user_input)
        print(f"输入: {user_input}")
        print(f"  选中工具: {result.tool_name}")
        print(f"  置信度: {result.confidence:.2f}")
        print(f"  提取参数: {result.arguments}")
        print()
