from rank_bm25 import BM25Okapi
import re

class KeywordRetriever:
    """关键词检索器（BM25）"""
    
    def __init__(self, documents: List[str]):
        """
        初始化检索器
        
        参数:
            documents: 文档列表
        """
        # 分词处理
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]
        
        # 构建BM25索引
        self.bm25 = BM25Okapi(self.tokenized_docs)
        self.documents = documents
    
    def _tokenize(self, text: str) -> List[str]:
        """简单分词"""
        # 转为小写，按空格和标点分割
        text = text.lower()
        tokens = re.findall(r'\w+', text)
        return tokens
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        执行关键词检索
        
        参数:
            query: 用户查询
            top_k: 返回结果数量
        
        返回:
            (文档内容, 分数)列表
        """
        # 对查询分词
        tokenized_query = self._tokenize(query)
        
        # 获取BM25得分
        scores = self.bm25.get_scores(tokenized_query)
        
        # 获取Top-K索引
        top_indices = scores.argsort()[::-1][:top_k]
        
        # 返回结果
        results = [
            (self.documents[i], scores[i])
            for i in top_indices
        ]
        
        return results
