class VectorDatabaseSelector:
    """向量数据库选型助手"""
    
    def __init__(self):
        self.recommendations = []
        
    def analyze(self, 
                vector_count: int,
                qps: int,
                latency_requirement: str,
                has_ops_team: bool,
                budget: str,
                need_geo_distribution: bool) -> dict:
        """
        分析并推荐合适的向量数据库
        
        参数:
            vector_count: 向量数量
            qps: 每秒查询数
            latency_requirement: 延迟要求 ('low'/<10ms, 'medium'/<50ms, 'high'/>50ms)
            has_ops_team: 是否有运维团队
            budget: 预算 ('low'/<$100/月, 'medium'/$100-500, 'high'/>$500)
            need_geo_distribution: 是否需要地理分布
        """
        # 步骤1：基于数据规模筛选
        candidates = self._filter_by_scale(vector_count)
        
        # 步骤2：基于延迟要求筛选
        candidates = self._filter_by_latency(candidates, latency_requirement)
        
        # 步骤3：基于运维能力筛选
        candidates = self._filter_by_ops(candidates, has_ops_team)
        
        # 步骤4：基于预算筛选
        candidates = self._filter_by_budget(candidates, budget)
        
        # 步骤5：考虑地理分布
        if need_geo_distribution:
            candidates = [c for c in candidates if c.get('geo_support', False)]
        
        return {
            "recommended": candidates[:3] if candidates else ["需评估"],
            "vector_count": vector_count,
            "qps": qps,
            "recommendations": self._generate_recommendations(candidates, vector_count, qps)
        }
    
    def _filter_by_scale(self, vector_count: int) -> list:
        """按数据规模筛选"""
        all_dbs = [
            {"name": "FAISS", "min_scale": 0, "max_scale": 10000000},
            {"name": "Chroma", "min_scale": 0, "max_scale": 100000},
            {"name": "Qdrant", "min_scale": 0, "max_scale": 10000000},
            {"name": "Milvus", "min_scale": 10000, "max_scale": 100000000},
            {"name": "Pinecone", "min_scale": 0, "max_scale": 100000000},
            {"name": "Weaviate", "min_scale": 0, "max_scale": 10000000},
            {"name": "Zilliz Cloud", "min_scale": 0, "max_scale": 100000000},
        ]
        
        return [db for db in all_dbs 
                if db["min_scale"] <= vector_count <= db["max_scale"]]
    
    def _filter_by_latency(self, candidates: list, latency: str) -> list:
        """按延迟要求筛选"""
        latency_map = {
            "low": ["FAISS", "Qdrant"],
            "medium": ["FAISS", "Qdrant", "Milvus", "Pinecone"],
            "high": ["Milvus", "Pinecone", "Weaviate", "Chroma"]
        }
        
        preferred = latency_map.get(latency, [])
        return [db for db in candidates if db["name"] in preferred]
    
    def _filter_by_ops(self, candidates: list, has_ops: bool) -> list:
        """按运维能力筛选"""
        if has_ops:
            return candidates
        else:
            # 无运维团队优先选择托管服务
            managed = ["Pinecone", "Zilliz Cloud", "Weaviate"]
            return [db for db in candidates if db["name"] in managed] + \
                   [db for db in candidates if db["name"] == "Chroma"]
    
    def _filter_by_budget(self, candidates: list, budget: str) -> list:
        """按预算筛选"""
        # 免费方案
        if budget == "low":
            return [db for db in candidates if db["name"] in ["FAISS", "Chroma", "Weaviate"]]
        return candidates
    
    def _generate_recommendations(self, candidates: list, 
                                  vector_count: int, qps: int) -> list:
        """生成推荐说明"""
        recommendations = []
        
        if not candidates:
            recommendations.append("建议联系厂商进行定制化评估")
            return recommendations
        
        for db in candidates[:3]:
            rec = {
                "database": db["name"],
                "reasons": [],
                "estimated_cost": self._estimate_cost(db["name"], vector_count, qps)
            }
            
            # 添加推荐理由
            if vector_count < 100000:
                rec["reasons"].append("适合小规模数据")
            elif vector_count < 1000000:
                rec["reasons"].append("支持中等规模数据")
            else:
                rec["reasons"].append("支持大规模数据")
            
            recommendations.append(rec)
        
        return recommendations
    
    def _estimate_cost(self, db_name: str, vector_count: int, qps: int) -> str:
        """估算成本"""
        costs = {
            "FAISS": "$50-100/月（服务器）",
            "Chroma": "$20-50/月（服务器）",
            "Qdrant": "$100-200/月",
            "Milvus": "$200-500/月",
            "Pinecone": "$150-400/月",
            "Weaviate": "$150-400/月",
            "Zilliz Cloud": "$100-300/月"
        }
        return costs.get(db_name, "待评估")


# 使用示例
if __name__ == "__main__":
    selector = VectorDatabaseSelector()
    
    # 场景1：初创公司
    print("=" * 70)
    print("场景1：初创公司 - 10万向量，10 QPS，低延迟要求，无运维团队")
    result = selector.analyze(
        vector_count=100000,
        qps=10,
        latency_requirement="low",
        has_ops_team=False,
        budget="low",
        need_geo_distribution=False
    )
    print(f"推荐: {result['recommended']}")
    
    # 场景2：中型企业
    print("\n" + "=" * 70)
    print("场景2：中型企业 - 100万向量，100 QPS，中等延迟要求，有运维团队")
    result = selector.analyze(
        vector_count=1000000,
        qps=100,
        latency_requirement="medium",
        has_ops_team=True,
        budget="medium",
        need_geo_distribution=False
    )
    print(f"推荐: {result['recommended']}")
    
    # 场景3：大型企业
    print("\n" + "=" * 70)
    print("场景3：大型企业 - 1000万向量，500 QPS，低延迟要求，需要全球分布")
    result = selector.analyze(
        vector_count=10000000,
        qps=500,
        latency_requirement="low",
        has_ops_team=True,
        budget="high",
        need_geo_distribution=True
    )
    print(f"推荐: {result['recommended']}")
