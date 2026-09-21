"""
YamlOutputParser实际应用
展示处理K8s部署配置的完整流程
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import YamlOutputParser
from typing import Dict, Any

# ============================================================
# 创建解析器
# ============================================================
parser = YamlOutputParser()

prompt = ChatPromptTemplate.from_template(
    "根据以下描述生成Kubernetes部署配置。\n\n"
    "需求：{requirements}\n\n"
    "{format_instructions}"
)

llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0)
chain = prompt | llm | parser

# ============================================================
# 应用部署需求
# ============================================================
requirements = """
创建一个名为 myapp 的 Deployment：
- 镜像：myapp:latest
- 副本数：3
- 容器端口：8080
- 资源限制：CPU 500m, 内存 512Mi
- 环境变量：APP_ENV=production
- 标签：app=myapp, version=v1
"""

result = chain.invoke({"requirements": requirements})

print("生成的K8s配置：")
print("-" * 40)

# 解析Deployment配置
def extract_k8s_config(yaml_data: Dict[str, Any]) -> None:
    """提取并显示K8s配置的关键信息"""
    for key, value in yaml_data.items():
        if isinstance(value, dict):
            print(f"{key}:")
            for k, v in value.items():
                if isinstance(v, dict):
                    print(f"  {k}:")
                    for kk, vv in v.items():
                        print(f"    {kk}: {vv}")
                elif isinstance(v, list):
                    print(f"  {k}: {v}")
                else:
                    print(f"  {k}: {v}")
        else:
            print(f"{key}: {value}")

extract_k8s_config(result)
