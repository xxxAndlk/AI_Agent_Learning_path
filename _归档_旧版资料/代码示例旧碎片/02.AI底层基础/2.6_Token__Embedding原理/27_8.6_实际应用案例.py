import numpy as np

class DocumentIndexer:
    """RAG文档索引器"""
    
    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
        self.model = AutoModel.from_pretrained("bert-base-chinese")
        self.doc_embeddings = []
        self.documents = []
    
    def add_documents(self, docs, chunk_size=512):
        """添加文档，自动分块"""
        for doc in docs:
            # 分块处理长文档
            chunks = self._chunk_text(doc, chunk_size)
            for chunk in chunks:
                emb = self._encode(chunk)
                self.doc_embeddings.append(emb)
                self.documents.append(chunk)
    
    def _chunk_text(self, text, max_length):
        """简单分块策略"""
        tokens = self.tokenizer.tokenize(text)
        chunks = []
        for i in range(0, len(tokens), max_length):
            chunk_tokens = tokens[i:i+max_length]
            chunks.append(self.tokenizer.convert_tokens_to_string(chunk_tokens))
        return chunks
    
    def _encode(self, text):
        """编码文本"""
        encoded = self.tokenizer(text, return_tensors="pt", truncation=True)
        with torch.no_grad():
            output = self.model(**encoded)
        return output.last_hidden_state[:, 0, :].numpy()
    
    def retrieve(self, query, top_k=3):
        """检索相关文档"""
        query_emb = self._encode(query)
        similarities = [
            np.dot(query_emb.flatten(), doc_emb.flatten()) 
            for doc_emb in self.doc_embeddings
        ]
        top_indices = np.argsort(similarities)[::-1][:top_k]
        return [self.documents[i] for i in top_indices]
