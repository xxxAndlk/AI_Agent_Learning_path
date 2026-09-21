from langchain_openai import ChatOpenAI

class LLMReranker:
    """基于LLM的重排序器"""
    
    def __init__(
        self,
        llm_model: str = "gpt-5.4-mini",
        temperature: float = 0
    ):
        """
        初始化重排序器
        
        参数:
            llm_model: LLM模型名称
            temperature: 温度参数
        """
        self.llm = ChatOpenAI(
            model_name=llm_model,
            temperature=temperature
        )
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        top_k: int = 5
    ) -> List[Dict]:
        """
        使用LLM重排序
        
        参数:
            query: 用户查询
            documents: 文档列表
            top_k: 返回结果数量
        
        返回:
            重排序后的结果
        """
        # 构建评估提示
        doc_list = "\n".join([
            f"[{i+1}] {doc[:200]}..."
            for i, doc in enumerate(documents)
        ])
        
        prompt = f"""请评估以下文档与查询的相关性。
        
查询: {query}

文档:
{doc_list}

请按照以下格式返回每个文档的相关性分数（0-10分）：
[序号]: 分数 - 理由

只返回分数和简要理由，不要其他内容。"""
        
        # 调用LLM
        response = self.llm.predict(prompt)
        
        # 解析结果
        results = []
        lines = response.strip().split('\n')
        for line in lines:
            if '[' in line and ']' in line:
                try:
                    idx = int(line.split('[')[1].split(']')[0]) - 1
                    score_part = line.split(':')[1].split('-')[0].strip()
                    score = float(score_part)
                    results.append({
                        'document': documents[idx],
                        'score': score
                    })
                except:
                    continue
        
        # 如果解析失败，使用默认分数
        if not results:
            results = [
                {'document': doc, 'score': 5.0}
                for doc in documents[:top_k]
            ]
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
