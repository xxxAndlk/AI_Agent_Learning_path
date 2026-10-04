"""
自定义解析器与LCEL集成
展示如何将自定义解析器用于实际应用
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import BaseOutputParser
from typing import List

# ============================================================
# 自定义解析器：步骤提取器
# ============================================================
class StepsParser(BaseOutputParser[List[dict]]):
    """
    步骤解析器
    解析操作步骤文本，返回结构化步骤列表
    """
    
    def parse(self, text: str) -> List[dict]:
        """解析步骤文本"""
        steps = []
        lines = text.strip().split('\n')
        
        current_step = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检测步骤编号
            import re
            step_match = re.match(r'^(\d+)[\.、\)]', line)
            
            if step_match:
                # 保存上一步
                if current_step:
                    steps.append(current_step)
                
                # 开始新步骤
                step_num = step_match.group(1)
                content = line[step_match.end():].strip()
                current_step = {
                    "step": int(step_num),
                    "action": content,
                    "details": []
                }
            elif current_step and line.startswith('-'):
                # 添加详情
                current_step["details"].append(line[1:].strip())
        
        # 保存最后一步
        if current_step:
            steps.append(current_step)
        
        return steps
    
    @property
    def _type(self) -> str:
        return "steps"

# ============================================================
# 集成到LCEL链
# ============================================================
parser = StepsParser()

prompt = ChatPromptTemplate.from_template(
    "请将以下操作过程分解为详细步骤。\n\n"
    "操作内容：{task}\n\n"
    "请按步骤说明，每步一行，步骤前加编号。可选的详细说明放在步骤后，以-开头。"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 执行链
# ============================================================
task = "如何用Python读取CSV文件并进行处理"

result = chain.invoke({"task": task})

print("解析的步骤：")
for step in result:
    print(f"\n步骤 {step['step']}: {step['action']}")
    for detail in step.get('details', []):
        print(f"  - {detail}")
