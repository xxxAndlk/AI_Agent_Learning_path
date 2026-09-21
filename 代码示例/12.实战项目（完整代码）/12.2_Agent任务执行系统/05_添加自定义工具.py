# 方式1：直接注册到Agent
def my_custom_tool(param: str) -> str:
    """自定义工具的文档描述"""
    return f"处理: {param}"

agent.add_tool("my_tool", my_custom_tool, "工具描述")

# 方式2：通过ToolRegistry注册（推荐）
registry = ToolRegistry()
registry.register("my_tool", my_custom_tool, "工具描述", 
                 category="custom", parameters={...})
