"""
GraphRAG基础实现
展示知识图谱与RAG的结合
"""

from typing import Dict, List, Tuple, Set  # 导入类型提示
from dataclasses import dataclass  # 导入dataclass装饰器

@dataclass
class Entity:
    """实体数据类"""
    id: str  # 实体ID
    name: str  # 实体名称
    entity_type: str  # 实体类型

@dataclass
class Relation:
    """关系数据类"""
    source: str  # 源实体ID
    target: str  # 目标实体ID
    relation_type: str  # 关系类型

class KnowledgeGraph:
    """知识图谱类"""
    
    def __init__(self):
        # 初始化实体字典和关系列表
        self.entities: Dict[str, Entity] = {}
        self.relations: List[Relation] = []
    
    def add_entity(self, entity_id: str, name: str, entity_type: str):
        """添加实体到图谱"""
        # 创建实体对象并存储到字典中
        self.entities[entity_id] = Entity(entity_id, name, entity_type)
    
    def add_relation(self, source: str, target: str, relation_type: str):
        """添加关系到图谱"""
        # 创建关系对象并添加到列表
        self.relations.append(Relation(source, target, relation_type))
    
    def get_neighbors(self, entity_id: str, depth: int = 1) -> Set[str]:
        """获取邻居实体
        
        参数:
            entity_id: 实体ID
            depth: 跳数深度
        返回:
            邻居实体ID集合
        """
        neighbors = set()  # 初始化邻居集合
        current = {entity_id}  # 初始为指定实体的单点集
        
        # 按指定深度进行BFS扩展
        for _ in range(depth):
            next_level = set()  # 下一层节点
            for eid in current:
                # 遍历所有关系，寻找邻居
                for rel in self.relations:
                    # 如果当前实体是关系的源头
                    if rel.source == eid:
                        next_level.add(rel.target)
                        neighbors.add(rel.target)
                    # 如果当前实体是关系的目标
                    elif rel.target == eid:
                        next_level.add(rel.source)
                        neighbors.add(rel.source)
            current = next_level  # 移动到下一层
        
        return neighbors


class GraphRAG:
    """GraphRAG系统类"""
    
    def __init__(self, kg: KnowledgeGraph, text_retriever):
        # 注入知识图谱和文本检索器
        self.kg = kg
        self.text_retriever = text_retriever
    
    def retrieve_with_graph(
        self, 
        query: str,
        use_graph_expansion: bool = True
    ) -> List[Dict]:
        """图增强检索
        
        参数:
            query: 查询文本
            use_graph_expansion: 是否使用图扩展
        返回:
            检索结果列表
        """
        # 步骤1：执行基础文本检索
        base_results = self.text_retriever.retrieve(query)
        
        # 如果不使用图扩展，直接返回基础结果
        if not use_graph_expansion:
            return base_results
        
        # 步骤2：图增强检索
        expanded_docs = []
        
        # 遍历基础检索结果的前3个
        for result in base_results[:3]:
            # 获取结果中的实体ID（简化处理，实际应使用NER提取）
            entity_id = result.get("entity_id", "")
            
            # 如果实体存在于知识图谱中
            if entity_id in self.kg.entities:
                # 扩展获取1跳邻居实体
                neighbors = self.kg.get_neighbors(entity_id, depth=1)
                
                # 遍历邻居实体
                for neighbor_id in neighbors:
                    if neighbor_id in self.kg.entities:
                        entity = self.kg.entities[neighbor_id]
                        # 添加邻居实体信息到扩展结果
                        expanded_docs.append({
                            "content": f"相关实体: {entity.name} ({entity.entity_type})",
                            "source": "graph",
                            "entity_id": neighbor_id
                        })
        
        # 合并基础结果和扩展结果，返回最多5个扩展结果
        return base_results + expanded_docs[:5]


# 使用示例
if __name__ == "__main__":
    # 构建示例知识图谱
    kg = KnowledgeGraph()
    
    # 添加实体
    kg.add_entity("e1", "Python", "编程语言")
    kg.add_entity("e2", "机器学习", "技术领域")
    kg.add_entity("e3", "TensorFlow", "框架")
    kg.add_entity("e4", "PyTorch", "框架")
    
    # 添加关系：表示实体之间的关联
    kg.add_relation("e1", "e2", "应用于")  # Python应用于机器学习
    kg.add_relation("e2", "e3", "使用")  # 机器学习使用TensorFlow
    kg.add_relation("e2", "e4", "使用")  # 机器学习使用PyTorch
    
    # 模拟文本检索器
    class MockTextRetriever:
        def retrieve(self, query):
            return [{"content": "Python机器学习相关", "entity_id": "e1"}]
    
    # 创建GraphRAG系统并测试
    graph_rag = GraphRAG(kg, MockTextRetriever())
    results = graph_rag.retrieve_with_graph("Python机器学习")
    
    # 打印检索结果
    print("GraphRAG检索结果:")
    for r in results:
        print(f"  - {r['content']}")
