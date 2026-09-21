from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from typing import List, Dict
import json

# ==================== 工具定义 ====================

@tool
def search_academic(query: str, max_results: int = 5) -> str:
    """学术搜索工具。适用于：查找论文、学术资料、研究成果
    
    Args:
        query: 搜索关键词
        max_results: 最大结果数
    """
    # 模拟学术搜索
    results = []
    for i in range(min(max_results, 3)):
        results.append(f"论文{i+1}: {query}相关研究 - 作者等, 2024")
    return "\n".join(results)

@tool
def search_web(query: str, source: str = "general") -> str:
    """网络搜索工具。适用于：查找最新新闻、博客、教程
    
    Args:
        query: 搜索关键词
        source: 来源类型 general/news/blog
    """
    sources = {
        "general": "综合搜索结果",
        "news": "最新新闻报道",
        "blog": "博客文章"
    }
    return f"{sources.get(source, '综合')}关于'{query}'的结果"

@tool
def search_code(query: str, language: str = "python") -> str:
    """代码搜索工具。适用于：查找示例代码、解决方案
    
    Args:
        query: 搜索关键词
        language: 编程语言
    """
    return f"代码示例 - {language}实现: \n# {query}的示例代码"

@tool
def summarize_text(text: str, max_length: int = 200) -> str:
    """文本摘要工具。将长文本压缩成简洁的摘要
    
    Args:
        text: 要摘要的文本
        max_length: 最大长度
    """
    # 简单模拟：提取第一句和生成总结
    sentences = text.split("\n")
    summary = f"摘要: {text[:max_length]}..."
    return summary

@tool
def save_to_file(content: str, filename: str = "research.md") -> str:
    """保存研究结果到文件
    
    Args:
        content: 要保存的内容
        filename: 文件名
    """
    try:
        # 实际保存文件
        # with open(filename, 'w', encoding='utf-8') as f:
        #     f.write(content)
        return f"已保存到: {filename}"
    except Exception as e:
        return f"保存失败: {e}"

# ==================== Agent配置 ====================

# 初始化工具列表
tools = [
    search_academic,
    search_web,
    search_code,
    summarize_text,
    save_to_file
]

# 初始化LLM
llm = ChatOpenAI(
    model="gpt-5.4",
    temperature=0.3
)

# 使用 create_agent 创建Agent（v1.x 推荐）
agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""你是一个专业的研究助手，帮助用户完成信息搜集、整理和报告生成。

工作流程：
1. 理解用户的研究主题
2. 使用多个搜索工具搜集相关信息（学术、网络、代码）
3. 对收集到的信息进行整理和摘要
4. 生成结构化的研究报告
5. 可以选择保存到文件

注意：
- 根据研究主题选择合适的搜索工具
- 对于技术主题，同时搜索学术资料和代码示例
- 保持客观和准确"""
)

# ==================== 使用示例 ====================

def run_research(query: str):
    """运行研究查询"""
    print(f"\n{'='*60}")
    print(f"研究主题: {query}")
    print('='*60)
    
    result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    
    print(f"\n{'='*60}")
    print("研究结果:")
    print('='*60)
    print(result["messages"][-1].content)
    
    return result

# 测试研究助手
if __name__ == "__main__":
    # 测试1: 技术研究
    run_research("Python异步编程的最佳实践")
    
    # 测试2: 学术研究
    run_research("深度学习在自然语言处理中的应用")
