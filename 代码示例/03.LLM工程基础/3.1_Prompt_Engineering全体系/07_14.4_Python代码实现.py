from openai import OpenAI
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json

client = OpenAI()

@dataclass
class SystemPromptConfig:
    """系统提示配置类"""
    role_name: str              # 角色名称
    primary_task: str           # 主要任务
    expertise: List[str]        # 专业领域
    constraints: List[str]      # 约束条件
    style: str                  # 风格描述
    output_format: Optional[str] = None  # 输出格式要求


class SystemPromptBuilder:
    """系统提示构建器

import matplotlib
import numpy
import pandas

    
    帮助构建有效的系统提示
    """
    
    def __init__(self):
        self.config: Optional[SystemPromptConfig] = None
    
    def set_role(self, role_name: str) -> 'SystemPromptBuilder':
        """设置角色名称"""
        self.config = SystemPromptConfig(
            role_name=role_name,
            primary_task="",
            expertise=[],
            constraints=[],
            style=""
        )
        return self
    
    def set_task(self, task: str) -> 'SystemPromptBuilder':
        """设置主要任务"""
        if self.config:
            self.config.primary_task = task
        return self
    
    def add_expertise(self, area: str) -> 'SystemPromptBuilder':
        """添加专业领域"""
        if self.config:
            self.config.expertise.append(area)
        return self
    
    def add_constraint(self, constraint: str) -> 'SystemPromptBuilder':
        """添加约束条件"""
        if self.config:
            self.config.constraints.append(constraint)
        return self
    
    def set_style(self, style: str) -> 'SystemPromptBuilder':
        """设置风格"""
        if self.config:
            self.config.style = style
        return self
    
    def set_output_format(self, format_str: str) -> 'SystemPromptBuilder':
        """设置输出格式"""
        if self.config:
            self.config.output_format = format_str
        return self
    
    def build(self) -> str:
        """构建系统提示"""
        if not self.config:
            return ""
        
        parts = []
        
        # 角色定义
        parts.append(f"你是一个{self.config.role_name}。")
        
        # 主要任务
        if self.config.primary_task:
            parts.append(f"你的主要任务是{self.config.primary_task}。")
        
        # 专业领域
        if self.config.expertise:
            parts.append(f"你的专业领域包括：{', '.join(self.config.expertise)}。")
        
        # 行为准则
        if self.config.style:
            parts.append(f"在回答问题时，你应当{self.config.style}。")
        
        # 约束条件
        if self.config.constraints:
            parts.append("\n行为约束：")
            for constraint in self.config.constraints:
                parts.append(f"- {constraint}")
        
        # 输出格式
        if self.config.output_format:
            parts.append(f"\n输出格式要求：{self.config.output_format}")
        
        return "\n".join(parts)


def create_code_assistant() -> str:
    """创建代码助手系统提示"""
    return SystemPromptBuilder() \
        .set_role("专业软件工程师") \
        .set_task("帮助用户解决编程问题、代码调试和软件设计") \
        .add_expertise("Python") \
        .add_expertise("JavaScript") \
        .add_expertise("数据结构与算法") \
        .add_expertise("系统设计") \
        .set_style("使用清晰、准确的技术语言，提供完整的代码示例和解释") \
        .add_constraint("只提供安全、合法的代码建议") \
        .add_constraint("不生成恶意代码或安全漏洞") \
        .add_constraint("对于不确定的问题，明确说明不确定性") \
        .set_output_format("代码使用markdown代码块格式，并在必要时提供注释") \
        .build()


def create_data_analyst() -> str:
    """创建数据分析助手系统提示"""
    return """你是一个专业的数据分析师。

你的主要任务是帮助用户进行数据分析、数据可视化和洞察发现。

你的专业领域包括：
- 统计分析
- 数据可视化
- 机器学习基础
- Python数据分析（pandas, numpy, matplotlib）

在回答问题时，你应当：
1. 基于数据和分析结果给出结论
2. 解释使用的分析方法及其适用性
3. 提供可执行的代码示例

行为约束：
- 不编造不存在的数据
- 明确说明统计假设和局限性
- 建议的结论必须有数据支持

输出格式要求：
- 关键数值使用表格或列表呈现
- 复杂分析提供Python代码
- 图表使用ASCII或描述性语言说明
"""


def create_translator() -> str:
    """创建翻译助手系统提示"""
    return SystemPromptBuilder() \
        .set_role("专业翻译助手") \
        .set_task("提供高质量的翻译服务") \
        .add_expertise("中英翻译") \
        .add_expertise("技术文档翻译") \
        .add_expertise("商务翻译") \
        .set_style("保持原文语义，遵循目标语言习惯") \
        .add_constraint("不添加解释性内容，如需说明使用括号") \
        .add_constraint("保留专业术语的标准译法") \
        .set_output_format("仅输出翻译内容，不添加额外说明") \
        .build()


class PromptTemplate:
    """提示模板类
    
    提供常用的提示模板
    """
    
    TEMPLATES = {
        "analysis": """你是一个专业的{role}。

背景：{context}

任务：{task}

请按照以下步骤进行分析：
1. 理解问题
2. 收集相关信息
3. 进行分析
4. 给出结论

输出格式：{format}""",
        
        "comparison": """比较以下两个选项：

选项A：{option_a}
选项B：{option_b}

请从以下维度进行比较：
- 优点
- 缺点
- 适用场景
- 建议

结论：{conclusion_format}""",
        
        "step_by_step": """请逐步解决以下问题：

问题：{problem}

请按步骤回答，每步都要有清晰的推理过程。""",
        
        "summarization": """请总结以下内容：

{content}

要求：
- 保留核心信息
- 简洁明了
- 不超过{length}字"""
    }
    
    @classmethod
    def get_template(cls, name: str) -> Optional[str]:
        """获取模板"""
        return cls.TEMPLATES.get(name)
    
    @classmethod
    def fill_template(
        cls, 
        name: str, 
        **kwargs
    ) -> str:
        """填充模板"""
        template = cls.get_template(name)
        if not template:
            return ""
        return template.format(**kwargs)


def test_system_prompts():
    """测试系统提示"""
    
    prompts = {
        "代码助手": create_code_assistant(),
        "数据分析师": create_data_analyst(),
        "翻译助手": create_translator()
    }
    
    for name, prompt in prompts.items():
        print(f"\n{'='*50}")
        print(f"{name}系统提示:")
        print('='*50)
        print(prompt[:200] + "..." if len(prompt) > 200 else prompt)
        
        # 测试使用
        response = client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": "你好，请介绍一下你自己"}
            ]
        )
        print(f"\n回复: {response.choices[0].message.content[:100]}...")
