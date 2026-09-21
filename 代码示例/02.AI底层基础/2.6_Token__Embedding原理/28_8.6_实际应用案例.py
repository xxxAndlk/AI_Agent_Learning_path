import torch
import torch.nn.functional as F

class QASystem:
    """问答系统"""
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
        self.model = AutoModel.from_pretrained("bert-base-chinese")
        self.qa_pairs = []  # (question, answer, embedding)
    
    def add_qa(self, question, answer):
        """添加问答对"""
        emb = self._encode(question)
        self.qa_pairs.append((question, answer, emb))
    
    def answer(self, query, threshold=0.7):
        """回答问题"""
        query_emb = self._encode(query)
        
        best_score = -1
        best_answer = "抱歉，我不理解您的问题。"
        
        for q, a, emb in self.qa_pairs:
            score = F.cosine_similarity(
                torch.from_numpy(query_emb), 
                torch.from_numpy(emb)
            ).item()
            if score > best_score:
                best_score = score
                best_answer = a if score > threshold else best_answer
        
        return best_answer, best_score
