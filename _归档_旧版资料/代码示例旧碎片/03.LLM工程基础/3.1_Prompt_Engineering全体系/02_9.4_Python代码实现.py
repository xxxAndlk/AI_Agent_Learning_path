from openai import OpenAI
import os
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from dotenv import load_dotenv

load_dotenv()

MODEL = os.getenv("MODEL", "deepseek-v4-flash")
API_KEY = os.getenv("API_KEY")
BASE_URL = os.getenv("URL")

client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL,
)

class NodeState(Enum):
    """节点状态枚举"""
    PENDING = "pending"        # 待处理
    EXPANDED = "expanded"      # 已扩展
    EVALUATED = "evaluated"    # 已评估
    SOLVED = "solved"          # 已解决
    FAILED = "failed"          # 失败

@dataclass
class ThoughtNode:
    """思维树节点类
    
    用于表示思维过程中的一个推理节点
    包含当前推理内容、子节点、评估分数和状态
    """
    content: str                        # 节点的推理内容
    parent: Optional['ThoughtNode'] = None  # 父节点引用
    children: List['ThoughtNode'] = field(default_factory=lambda: [])  # 子节点列表
    score: float = 0.0                  # 评估分数
    state: NodeState = NodeState.PENDING  # 节点状态
    depth: int = 0                      # 节点深度
    
    def add_child(self, child: 'ThoughtNode') -> None:
        """添加子节点
        
        Args:
            child: 要添加的子节点
        """
        child.parent = self
        child.depth = self.depth + 1
        self.children.append(child)
    
    def get_path(self) -> List[str]:
        """获取从根节点到当前节点的完整路径
        
        Returns:
            路径上的所有推理内容列表
        """
        path: List[str] = []
        current = self
        while current:
            path.insert(0, current.content)
            current = current.parent
        return path


class TreeOfThoughts:
    """思维树实现类
    
    实现了ToT的核心逻辑：多路径生成、评估、选择和回溯
    """
    
    def __init__(
        self, 
        client: OpenAI,
        model: str = MODEL,
        max_depth: int = 4,
        branching_factor: int = 3,
        max_trials: int = 3
    ):
        """
        初始化思维树
        
        Args:
            client: OpenAI客户端实例
            model: 使用的模型名称
            max_depth: 最大树深度
            branching_factor: 分支因子（每个节点生成的子节点数）
            max_trials: 最大尝试次数
        """
        self.client = client
        self.model = model
        self.max_depth = max_depth
        self.branching_factor = branching_factor
        self.max_trials = max_trials
    
    def generate_thoughts(
        self, 
        prompt: str, 
        context: List[str],
        num_thoughts: int = 3
    ) -> List[str]:
        """生成多个思考分支
        
        基于当前上下文，生成多个可能的推理方向
        
        Args:
            prompt: 当前问题或任务描述
            context: 之前的推理路径上下文
            num_thoughts: 要生成的思考数量
            
        Returns:
            生成的思考列表
        """
        # 构建包含上下文的提示
        context_str = "\n".join([f"路径{i+1}: {c}" for i, c in enumerate(context)])
        
        full_prompt = f"""你正在解决一个问题。请提供{num_thoughts}个不同的思考方向或解决方案。

                    当前问题: {prompt}

                    已有的推理路径:
                    {context_str}

                    请为每个思考方向提供一个简短但有意义的推理步骤。
                    格式要求：每个思考单独一行，以编号开头。
                    """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": full_prompt}],
            temperature=0.7
        )
        
        # 解析生成的思考
        thoughts: List[str] = []
        content = response.choices[0].message.content
        if not content:
            return []

        for line in content.strip().split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                thought = line.lstrip('0123456789.-) ').strip()
                if thought:
                    thoughts.append(thought)

        return thoughts[:num_thoughts]
    
    def evaluate_thought(
        self, 
        prompt: str, 
        thought: str,
        context: List[str]
    ) -> float:
        """评估单个思考的价值
        
        使用LLM来评估某个思考方向是否有前景
        
        Args:
            prompt: 原始问题
            thought: 要评估的思考
            context: 推理上下文
            
        Returns:
            评估分数（0-1之间）
        """
        context_str = "\n".join(context)
        
        evaluation_prompt = f"""请评估以下思考对于解决问题的价值。

        原始问题: {prompt}

        当前推理路径:
        {context_str}

        待评估思考: {thought}

        请从以下维度进行评分（0-1分）：
        1. 可行性：这个思考是否可行？
        2. 完整性：这个思考是否完整？
        3. 前景：这个思考是否可能导向正确答案？
        4. 多样性：这个思考是否与其他思考不同？

        请直接输出一个0-1之间的综合分数，只输出数字，不要其他内容。
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
            return max(0.0, min(1.0, score))
        except ValueError:
            return 0.5  # 默认中等分数
    
    def solve(
        self, 
        problem: str,
        initial_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """使用思维树解决问题
        
        主求解函数，执行完整的ToT搜索过程
        
        Args:
            problem: 要解决的问题
            initial_prompt: 可选的初始提示
            
        Returns:
            包含解决方案和搜索过程的字典
        """
        # 创建根节点
        approx_calls = sum(self.branching_factor ** d for d in range(self.max_depth)) * 2
        print(f"开始 ToT 搜索 (最大深度={self.max_depth}, 分支因子={self.branching_factor}, 预计API调用~{approx_calls}次)")
        root = ThoughtNode(content=problem, depth=0)
        
        # 广度优先搜索
        queue = [root]
        best_solution = None
        best_score = 0.0
        
        while queue:
            current = queue.pop(0)

            # 已达最大深度，不再扩展
            if current.depth >= self.max_depth:
                continue

            print(f"  [depth {current.depth}] 正在生成分支...", end=" ")
            # 生成多个思考
            context = current.get_path()
            thoughts = self.generate_thoughts(
                problem,
                context[:-1] if context else [],
                self.branching_factor
            )
            print(f"获得 {len(thoughts)} 个分支")

            # 评估并添加子节点
            for i, thought in enumerate(thoughts):
                print(f"  [depth {current.depth}] 评估分支 {i+1}/{len(thoughts)}...", end=" ")
                child = ThoughtNode(content=thought, parent=current)
                score = self.evaluate_thought(problem, thought, context)
                child.score = score
                current.add_child(child)
                print(f"分数 {score:.2f}")

                # 更新最佳解
                if score > best_score:
                    best_score = score
                    best_solution = child.get_path()

                # 达到叶节点则标记
                if current.depth + 1 >= self.max_depth:
                    child.state = NodeState.SOLVED if score > 0.7 else NodeState.FAILED

            # 将子节点加入队列（按分数排序）
            queue.extend(sorted(current.children, key=lambda x: x.score, reverse=True))
            print(f"  队列中还有 {len(queue)} 个节点待处理")
        
        return {
            "solution": best_solution,
            "score": best_score,
            "tree": root,
            "total_nodes": self._count_nodes(root)
        }
    
    def _count_nodes(self, node: ThoughtNode) -> int:
        """统计节点总数"""
        count = 1
        for child in node.children:
            count += self._count_nodes(child)
        return count


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


def tot_example():
    """ToT 使用示例"""

    tot = TreeOfThoughts(
        client=client,
        model=MODEL,
        max_depth=3,
        branching_factor=3,
    )

    problem = """小明有100元，要买以下商品：
    - 苹果每个3元
    - 香蕉每个2元
    - 橙子每个1元

    刚好花完100元，且必须包含至少10个水果。请问各有几个？"""

    result = tot.solve(problem)

    print("=" * 50)
    print("Tree of Thoughts 结果")
    print("=" * 50)
    print(f"最佳解决方案: {result['solution']}")
    print(f"评估分数: {result['score']:.2f}")
    print(f"探索节点数: {result['total_nodes']}")


def main():
    if not check_client():
        print("\nClient check failed. Check your .env settings.")
        return
    print("\nClient ready. Starting ToT example...\n")
    tot_example()


if __name__ == "__main__":
    main()
