"""
Multi-hop RAG实现
支持多步推理的检索增强生成
"""

from typing import List, Dict, Optional  # 导入类型提示
from dataclasses import dataclass  # 导入dataclass装饰器

@dataclass
class ReasoningStep:
    """推理步骤数据类"""
    step_number: int  # 步骤编号
    query: str  # 当前步骤的查询
    evidence: List[str]  # 收集到的证据
    intermediate_answer: str  # 中间答案

class MultiHopRAG:
    """多跳RAG系统"""
    
    def __init__(self, retriever):
        self.retriever = retriever  # 注入检索器
        self.max_hops = 3  # 最大跳数设置为3
    
    def reason(self, initial_query: str) -> Dict:
        """多步推理"""
        steps = []  # 存储所有推理步骤
        current_query = initial_query  # 当前查询初始化为原始查询
        
        # 迭代执行多跳推理
        for hop in range(self.max_hops):
            # 使用检索器获取相关文档
            docs = self.retriever.retrieve(current_query)
            # 提取前3个文档的内容作为证据
            evidence = [d["content"] for d in docs[:3]]
            
            # 生成中间答案（此处简化处理）
            intermediate = f"第{hop+1}步找到的相关信息"
            
            # 创建推理步骤对象并添加到步骤列表
            step = ReasoningStep(
                step_number=hop + 1,
                query=current_query,
                evidence=evidence,
                intermediate_answer=intermediate
            )
            steps.append(step)
            
            # 如果不是最后一步，生成下一步的查询
            if hop < self.max_hops - 1:
                # 基于中间答案构造新的查询
                current_query = f"基于{intermediate}的后续问题"
        
        # 返回包含所有步骤和最终答案的结果
        return {
            "steps": steps,
            "final_answer": f"综合{len(steps)}步推理的结果"
        }


# 使用示例
if __name__ == "__main__":
    # 创建模拟的检索器
    class MockRetriever:
        def retrieve(self, query):
            # 返回模拟的检索结果
            return [{"content": f"关于'{query}'的相关文档"}]
    
    # 创建多跳RAG系统并测试
    rag = MultiHopRAG(MockRetriever())
    result = rag.reason("比较Python和Java在企业级开发中的应用")
    
    # 打印推理结果
    print(f"多跳推理结果：")
    for step in result["steps"]:
        print(f"  步骤{step.step_number}: {step.query}")
