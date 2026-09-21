from openai import OpenAI
import os
from typing import List, Dict, Any, Optional, Set, cast
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv
import uuid

load_dotenv()

MODEL = os.getenv("MODEL", "deepseek-v4-flash")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("URL")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)


class NodeType(str, Enum):
    """节点类型枚举"""
    REASON = "reason"        # 推理节点
    AGGREGATE = "aggregate"  # 聚合节点
    EVALUATE = "evaluate"    # 评估节点
    FINAL = "final"          # 最终节点


class Strategy(str, Enum):
    """聚合策略枚举"""
    COMBINE = "combine"      # 综合策略
    SELECT = "select"        # 选择策略


@dataclass
class GraphNode:
    """图节点类

    表示思维图中的一个节点，可以是推理、聚合或评估节点

    示例：
    节点A → 节点B → 节点C

    对于节点B：
    - 前驱节点：{A}（节点B依赖A的输出）
    - 后继节点：{C}（节点C依赖B的输出）
    """
    node_id: str                                      # 唯一标识符
    content: str                                      # 节点内容
    node_type: 'NodeType' = NodeType.REASON            # 节点类型
    predecessors: Set[str] = field(default_factory=lambda: cast(Set[str], set()))  # 前驱节点ID集合
    successors: Set[str] = field(default_factory=lambda: cast(Set[str], set()))    # 后继节点ID集合
    score: float = 0.0                             # 节点评分
    processed: bool = False                        # 是否已处理
    metadata: Dict[str, Any] = field(default_factory=lambda: cast(Dict[str, Any], dict()))  # 元数据


class GraphOfThoughts:
    """
    思维图实现类

    实现基于图结构的推理框架，支持节点的创建、连接、聚合和评估
    """

    def __init__(
        self,
        client: OpenAI,
        model: str = MODEL
    ):
        """初始化思维图"""
        self.client = client
        self.model = model
        self.nodes: Dict[str, GraphNode] = {}
        self.node_counter = 0

    def _generate_id(self) -> str:
        """生成唯一节点ID"""
        self.node_counter += 1
        node_id = f"node_{self.node_counter}_{str(uuid.uuid4()).replace('-', '')[:10]}"
        return node_id

    def add_node(
        self,
        content: str,
        node_type: NodeType = NodeType.REASON,
        predecessors: Optional[List[str]] = None
    ) -> str:
        """添加节点到图中

        Args:
            content: 节点内容
            node_type: 节点类型
            predecessors: 前驱节点ID列表

        Returns:
            新增节点的ID
        """
        node_id = self._generate_id()
        node = GraphNode(
            node_id=node_id,
            content=content,
            node_type=node_type,
            predecessors=set(predecessors) if predecessors else set()
        )

        # 把当前节点添加到所有前驱节点的后继节点列表中
        if predecessors:
            for pred_id in predecessors:
                if pred_id in self.nodes:
                    self.nodes[pred_id].successors.add(node_id)

        self.nodes[node_id] = node
        return node_id

    def get_node_content(self, node_id: str) -> str:
        """
        获取节点及其前驱节点的完整内容

        Args:
            node_id: 节点ID

        Returns:
            完整的上下文内容
        """
        if node_id not in self.nodes:
            return ""

        node = self.nodes[node_id]
        contents: List[str] = [node.content]

        visited: Set[str] = set()
        to_visit: List[str] = list(node.predecessors)

        while to_visit:
            pred_id = to_visit.pop(0)
            if pred_id in visited:
                continue
            visited.add(pred_id)

            if pred_id in self.nodes:
                contents.insert(0, self.nodes[pred_id].content)
                to_visit.extend(self.nodes[pred_id].predecessors)

        return "\n".join(contents)

    def expand_node(
        self,
        node_id: str,
        num_expansions: int = 3
    ) -> List[str]:
        """扩展节点，生成多个思考分支

        Args:
            node_id: 要扩展的节点ID
            num_expansions: 扩展数量

        Returns:
            新增节点的ID列表
        """
        if node_id not in self.nodes:
            return []

        source_node = self.nodes[node_id]

        expansion_prompt = f"""基于以下推理步骤，请提供{num_expansions}个不同的扩展方向或下一步推理：

当前推理: {source_node.content}

请直接给出{num_expansions}个扩展方向，每个一行。
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": expansion_prompt}],
            temperature=0.7
        )

        content = response.choices[0].message.content
        if not content:
            return []

        new_node_ids: List[str] = []
        for line in content.strip().split('\n'):
            line = line.strip()
            if line:
                thought = line.lstrip('0123456789.-) ').strip()
                if thought:
                    node_id_new = self.add_node(
                        content=thought,
                        node_type=NodeType.REASON,
                        predecessors=[node_id]
                    )
                    new_node_ids.append(node_id_new)

        source_node.processed = True
        return new_node_ids

    def aggregate_nodes(
        self,
        node_ids: List[str],
        strategy: Strategy = Strategy.COMBINE
    ) -> Optional[str]:
        """聚合多个节点

        将多个节点的推理结果聚合为一个综合的结论

        Args:
            node_ids: 要聚合的节点ID列表
            strategy: 聚合策略

        Returns:
            聚合后的新节点ID
        """
        if not node_ids or not all(nid in self.nodes for nid in node_ids):
            return None

        contents = [self.nodes[nid].content for nid in node_ids]

        if strategy == Strategy.COMBINE:
            aggregation_prompt = f"""请综合以下{len(contents)}个推理方向，给出一个综合的结论：

{"\n".join([f"{i+1}. {c}" for i, c in enumerate(contents)])}

综合结论应该：
- 吸收各方向的优点
- 解决可能的冲突
- 提供一个完整的答案
"""
        elif strategy == Strategy.SELECT:
            aggregation_prompt = f"""请从以下{len(contents)}个选项中选择最佳的一个，并说明理由：

{"\n".join([f"{i+1}. {c}" for i, c in enumerate(contents)])}

直接给出选择的那个选项。
"""
        else:
            aggregation_prompt = f"请分析以下内容并给出评估：\n{"\n".join(contents)}"

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": aggregation_prompt}],
            temperature=0.3
        )

        agg_content = response.choices[0].message.content
        if not agg_content:
            return None

        aggregated_content = agg_content.strip()

        agg_node_id = self.add_node(
            content=aggregated_content,
            node_type=NodeType.AGGREGATE,
            predecessors=node_ids
        )

        return agg_node_id

    def evaluate_path(self, node_id: str) -> float:
        """评估从根节点到指定节点的路径质量

        Args:
            node_id: 目标节点ID

        Returns:
            路径评分（0-1）
        """
        if node_id not in self.nodes:
            return 0.0

        path_contents = self.get_node_content(node_id)

        evaluation_prompt = f"""请评估以下推理路径的质量（0-1分）：

{path_contents}

只输出一个数字，表示推理的正确性和完整性。
"""

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": evaluation_prompt}],
            temperature=0.0
        )

        content = response.choices[0].message.content
        if not content:
            return 0.5

        try:
            score = float(content.strip())
            self.nodes[node_id].score = max(0.0, min(1.0, score))
            return self.nodes[node_id].score
        except ValueError:
            return 0.5

    def get_best_solution(self) -> Optional[Dict[str, Any]]:
        """获取最佳解决方案

        遍历所有最终节点，返回评分最高的

        Returns:
            包含最佳解的字典
        """
        candidates: List[Dict[str, Any]] = []

        for node_id, node in self.nodes.items():
            if node.node_type in [NodeType.FINAL, NodeType.AGGREGATE] or not node.successors:
                score = self.evaluate_path(node_id)
                candidates.append({
                    "node_id": node_id,
                    "content": node.content,
                    "score": score,
                    "path": self.get_node_content(node_id)
                })

        if not candidates:
            return None

        best = max(candidates, key=lambda x: x["score"])
        return best

    def visualize(self) -> str:
        """生成图的文本可视化

        Returns:
            图结构的文本表示
        """
        lines = ["Graph of Thoughts 可视化:", "=" * 40]

        for node_id, node in self.nodes.items():
            node_type_indicator = {
                NodeType.REASON: "○",
                NodeType.AGGREGATE: "◇",
                NodeType.EVALUATE: "□",
                NodeType.FINAL: "★"
            }.get(node.node_type, "○")

            line = f"{node_type_indicator} [{node_id}] {node.content[:50]}"
            if len(node.content) > 50:
                line += "..."
            line += f" (score: {node.score:.2f})"

            if node.predecessors:
                line += f" <- {', '.join(node.predecessors)}"

            lines.append(line)

        return "\n".join(lines)


def check_client() -> bool:
    """检查 client 是否能成功发送请求"""
    print(f"Model: {MODEL}")
    print(f"Base URL: {BASE_URL}")
    print("Testing connection...", end=" ")

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "ping"}],
            max_tokens=10,
        )
        reply = response.choices[0].message.content
        print(f"OK (reply: {reply})")
        return True
    except Exception as e:
        print(f"FAILED: {e}")
        return False


def got_example():
    """GoT使用示例"""

    got = GraphOfThoughts(client=client, model=MODEL)

    print("开始 GoT 搜索...")
    print("  预计 API 调用: 1(根扩展) + 3×1(子扩展) + 3×1(聚合) + 评估 ≈ ~10 次")
    print("  阶段1: 创建根节点")

    root_id = got.add_node(
        content="如何设计一个高效的太阳能发电系统？需要考虑成本、效率和可靠性。",
        node_type=NodeType.REASON
    )
    print(f"  根节点已创建 (id: {root_id})")
    print("  阶段2: 扩展根节点 → 3 个分支...")

    first_level_ids = got.expand_node(root_id, num_expansions=3)
    print(f"  根节点扩展完成 → {len(first_level_ids)} 个分支")

    for i, node_id in enumerate(first_level_ids):
        print(f"  阶段3: 扩展分支 {i+1}/{len(first_level_ids)}...")
        second_level = got.expand_node(node_id, num_expansions=2)
        print(f"    获得 {len(second_level)} 个子分支")

        if len(second_level) >= 2:
            print("    聚合子分支...")
            got.aggregate_nodes(second_level, strategy=Strategy.COMBINE)
            print("    聚合完成")

    print("  阶段4: 评估所有路径获取最佳方案...")
    best = got.get_best_solution()

    print("\n" + "=" * 50)
    print("Graph of Thoughts 结果")
    print("=" * 50)
    print(got.visualize())
    print("\n最佳方案:")
    if best:
        print(best["content"])
        print(f"评分: {best['score']:.2f}")
    else:
        print("无")


def main():
    if not check_client():
        print("\nClient check failed. Check your .env settings.")
        return
    print("\nClient ready. Starting GoT example...\n")
    got_example()


if __name__ == "__main__":
    main()
