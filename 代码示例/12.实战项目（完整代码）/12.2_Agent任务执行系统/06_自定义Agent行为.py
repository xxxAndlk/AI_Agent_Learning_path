class CustomAgent(TaskExecutionAgent):
    """自定义Agent示例"""
    
    def register_tools(self) -> None:
        # 首先调用父类方法
        super().register_tools()
        
        # 添加自定义工具
        self.add_tool("custom_tool", self._custom_tool, "自定义工具")
    
    def _custom_tool(self, param: str) -> str:
        # 实现自定义逻辑
        return "自定义结果"
    
    def get_system_prompt(self) -> str:
        # 获取基础提示
        prompt = super().get_system_prompt()
        
        # 添加自定义指令
        prompt += "\n特别说明：你还可以使用 custom_tool 工具。\n"
        
        return prompt
