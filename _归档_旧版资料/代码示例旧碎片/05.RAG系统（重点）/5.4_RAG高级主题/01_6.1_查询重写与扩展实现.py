"""
查询重写与扩展示例
通过优化查询提高检索精度
"""

from typing import List, Dict
import numpy as np

class QueryProcessor:
    """查询处理器：用于对用户查询进行重写、扩展和分解"""
    
    def __init__(self, llm_client=None):
        """
        初始化查询处理器
        
        参数:
            llm_client: LLM客户端，用于查询重写（可选，如果不使用LLM功能可传None）
        """
        self.llm = llm_client  # 保存LLM客户端引用，后续用于HyDE等高级功能
        
        # 停用词集合：这些词在检索中意义不大，可以过滤掉以提高检索精度
        # 包含常见的中文停用词，如助词、介词、常见动词等
        self.stopwords = set(['的', '了', '在', '是', '我', '有', '和', '就', '不', '人', 
                              '都', '一', '一个', '上', '也', '很', '到', '说', '要', '去', 
                              '你', '会', '着', '没有', '看', '好', '自己', '这'])
    
    def expand_query(self, query: str, expansion_method: str = "synonym") -> List[str]:
        """
        查询扩展：将原始查询扩展为多个相关查询，提高检索覆盖率
        
        参数:
            query: 用户输入的原始查询字符串
            expansion_method: 扩展方法选择，可选值：
                - "synonym": 基于同义词词典的简单扩展
                - "hyde": 基于LLM生成假设文档的HyDE方法
        返回:
            expanded_queries: 扩展后的查询列表，最多返回5个
        """
        expanded_queries = [query]  # 首先包含原始查询，确保不丢失原始意图
        
        # 方法1：基于同义词的扩展
        if expansion_method == "synonym":
            # 定义同义词词典： key是原始词，value是同义词列表
            synonym_dict = {
                "大模型": ["LLM", "大语言模型", "GPT"],
                "微调": ["fine-tuning", "迁移学习", "适配"],
                "部署": ["上线", "发布", "生产环境"],
                "性能": ["速度", "效率", "吞吐量"],
            }
            
            # 遍历同义词词典，查找查询中是否有匹配的关键词
            for key, synonyms in synonym_dict.items():
                if key in query:  # 如果查询中包含词典中的词
                    for syn in synonyms:  # 遍历该词的同义词列表
                        new_query = query.replace(key, syn)  # 用同义词替换原词
                        if new_query not in expanded_queries:  # 避免重复添加
                            expanded_queries.append(new_query)
        
        # 方法2：HyDE（Hypothetical Document Embedding）扩展
        elif expansion_method == "hyde":
            # HyDE的核心思想：让LLM生成一个假设的"理想答案"，用这个假设答案来检索
            # 这样可以利用LLM的生成能力来引导检索方向
            if self.llm:  # 只有配置了LLM客户端才能使用HyDE
                hypothetical_doc = self._generate_hypothetical_doc(query)
                expanded_queries.append(hypothetical_doc)
        
        return expanded_queries[:5]  # 限制返回数量，最多5个扩展查询，避免过多影响效率
    
    def _generate_hypothetical_doc(self, query: str) -> str:
        """
        生成假设文档（HyDE方法的内部实现）
        
        参数:
            query: 原始查询
        返回:
            假设的理想答案文档
        """
        # 构建提示词，引导LLM生成可能包含答案的假设文档
        prompt = f"基于查询'{query}'，生成一段可能包含答案的文本："
        # 这里简化处理，实际应用中应该调用真实的LLM API
        # 真实实现会发送prompt给LLM，获取生成的假设文档，然后用它进行向量检索
        return f"关于'{query}'的信息：这是一个相关的假设文档内容。"
    
    def rewrite_query(self, query: str, context: str = "") -> str:
        """
        查询重写：将用户查询改写为更简洁、更适合检索的形式
        
        参数:
            query: 原始查询
            context: 上下文信息（可选，用于更精准的重写）
        返回:
            重写后的查询字符串
        """
        # 第1步：分词 - 将查询按空格分割成单词列表
        words = query.split()
        
        # 第2步：过滤停用词 - 移除常见但检索意义不大的词
        filtered_words = [w for w in words if w not in self.stopwords]
        
        # 第3步：提取关键词 - 筛选长度大于1的词（过滤单字）
        keywords = [w for w in filtered_words if len(w) > 1]
        
        # 第4步：重新组合 - 用空格连接关键词
        # 如果过滤后没有剩余关键词，则返回原始查询
        return " ".join(keywords) if keywords else query
    
    def decompose_query(self, query: str) -> List[str]:
        """
        查询分解：将复杂查询拆分为多个简单子查询
        
        适用场景：
        - 比较类查询："比较Python和Go的性能" -> 拆分为多个子查询
        - 多实体查询
        - 多意图查询
        
        参数:
            query: 复杂查询字符串
        返回:
            子查询列表
        """
        # 检测是否是比较类查询
        if "比较" in query or "vs" in query.lower():
            # 提取比较对象：去掉"比较"字样，按"和"分割
            parts = query.replace("比较", "").split("和")
            
            # 确保正好分割为两个部分
            if len(parts) == 2:
                a, b = parts[0].strip(), parts[1].strip()
                # 生成4个子查询：分别询问两者的优点和缺点
                return [
                    f"{a}的优点",
                    f"{a}的缺点",
                    f"{b}的优点",
                    f"{b}的缺点"
                ]
        
        # 如果不是比较类查询，返回原始查询（不分解）
        return [query]


# ==================== 使用示例 ====================
if __name__ == "__main__":
    # 创建查询处理器实例
    processor = QueryProcessor()
    
    # 示例1：查询扩展
    query = "大模型微调技术"
    expanded = processor.expand_query(query, "synonym")
    print(f"原始查询: {query}")
    print(f"扩展查询: {expanded}")
    # 输出可能包含: ["大模型微调技术", "LLM微调技术", "大语言模型微调技术", ...]
    
    # 示例2：查询分解
    complex_query = "比较Python和Go的性能"
    sub_queries = processor.decompose_query(complex_query)
    print(f"\n子查询: {sub_queries}")
    # 输出: ["Python的优点", "Python的缺点", "Go的优点", "Go的缺点"]
