"""
综合示例：智能配置生成器
展示XML、YAML、JSON解析器的综合应用
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import (
    JsonOutputParser,
    XmlOutputParser,
    YamlOutputParser
)
from typing import Dict, Any

# ============================================================
# 配置生成器实现
# ============================================================

class ConfigGenerator:
    """智能配置生成器"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
        self.parsers = {
            "json": JsonOutputParser(),
            "xml": XmlOutputParser(),
            "yaml": YamlOutputParser()
        }
    
    def generate(self, format_type: str, description: str) -> Dict[str, Any]:
        """
        生成配置
        
        Args:
            format_type: 输出格式 (json/xml/yaml)
            description: 配置描述
        
        Returns:
            解析后的配置字典
        """
        format_type = format_type.lower()
        if format_type not in self.parsers:
            raise ValueError(f"不支持的格式: {format_type}")
        
        parser = self.parsers[format_type]
        
        prompt = ChatPromptTemplate.from_template(
            "根据以下描述生成{format}格式的配置。\n\n"
            "配置需求：{description}\n\n"
            "{format_instructions}"
        )
        
        chain = prompt | self.llm | parser
        
        result = chain.invoke({
            "format": format_type.upper(),
            "description": description
        })
        
        return result
    
    def generate_all_formats(self, description: str) -> Dict[str, Dict[str, Any]]:
        """生成所有格式的配置"""
        results = {}
        
        for format_type in ["json", "xml", "yaml"]:
            try:
                results[format_type] = self.generate(format_type, description)
            except Exception as e:
                results[format_type] = {"error": str(e)}
        
        return results

# ============================================================
# 使用配置生成器
# ============================================================

generator = ConfigGenerator()

description = """
生成一个Web应用服务器配置：
- 应用名称：MyWebApp
- 端口：8080
- 数据库连接池最大连接数：20
- 启用缓存
- 日志级别：INFO
"""

print("生成配置...")
print("=" * 50)

# 生成所有格式
all_configs = generator.generate_all_formats(description)

for format_type, config in all_configs.items():
    print(f"\n{format_type.upper()} 格式:")
    print("-" * 30)
    import json
    print(json.dumps(config, indent=2, ensure_ascii=False))
