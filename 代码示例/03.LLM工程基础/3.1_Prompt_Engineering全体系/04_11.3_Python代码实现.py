from openai import OpenAI
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
import random
import re

client = OpenAI()

@dataclass
class PromptCandidate:
    """提示候选类
    
    表示一个提示词候选及其评估结果
    """
    prompt: str                              # 提示词内容
    score: float = 0.0                       # 评估分数
    examples: List[Dict[str, str]] = field(default_factory=list)  # 测试用例
    feedback: str = ""                       # 反馈信息


class AutomaticPromptEngineer:
    """自动提示工程工具类
    
    实现提示的自动生成、评估和优化
    """
    
    def __init__(
        self, 
        client: OpenAI,
        model: str = "gpt-5.4-mini"
    ):
        """初始化APE工具"""
        self.client = client
        self.model = model
        self.population: List[PromptCandidate] = []
    
    def generate_initial_prompts(
        self, 
        task_description: str,
        num_prompts: int = 5
    ) -> List[str]:
        """生成初始提示候选
        
        使用LLM生成多个不同风格的初始提示
        
        Args:
            task_description: 任务描述
            num_prompts: 生成数量
            
        Returns:
            提示列表
        """
        generation_prompt = f"""请为以下任务生成{num_prompts}个不同的提示词。
要求：每个提示词风格不同（有的简洁，有的详细，有的正式，有的口语）。

任务: {task_description}

输出格式：每个提示占一行，不要编号。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": generation_prompt}],
            temperature=0.8
        )
        
        prompts = []
        for line in response.choices[0].message.content.strip().split('\n'):
            line = line.strip()
            if line and len(line) > 10:
                # 清理可能的前缀
                prompt = re.sub(r'^\d+[\.\)]\s*', '', line)
                prompts.append(prompt)
        
        return prompts[:num_prompts]
    
    def evaluate_prompt(
        self, 
        prompt: str, 
        test_cases: List[Dict[str, str]],
        evaluation_metric: str = "accuracy"
    ) -> float:
        """评估提示词的效果
        
        在测试用例上运行提示，返回评估分数
        
        Args:
            prompt: 要评估的提示
            test_cases: 测试用例列表 [{"input": "...", "expected": "..."}]
            evaluation_metric: 评估指标
            
        Returns:
            评估分数（0-1）
        """
        if not test_cases:
            return 0.5
        
        correct = 0
        
        for test_case in test_cases:
            # 构建完整的提示（包含测试输入）
            full_prompt = f"{prompt}\n\n输入: {test_case['input']}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": full_prompt}],
                temperature=0.0
            )
            
            output = response.choices[0].message.content.strip()
            
            # 简单的匹配评估（实际应用中可能需要更复杂的评估）
            if test_case.get('expected', '').lower() in output.lower():
                correct += 1
        
        return correct / len(test_cases)
    
    def evolve_prompt(
        self, 
        prompt: str, 
        feedback: str,
        mutation_type: str = "improve"
    ) -> str:
        """演进提示词
        
        基于反馈对提示进行改进
        
        Args:
            prompt: 原始提示
            feedback: 反馈信息
            mutation_type: 演进类型
            
        Returns:
            改进后的提示
        """
        evolution_prompt = f"""请根据以下反馈改进提示词。

原始提示: {prompt}

反馈: {feedback}

请直接输出改进后的提示词，只输出提示词本身，不要其他解释。
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": evolution_prompt}],
            temperature=0.5
        )
        
        return response.choices[0].message.content.strip()
    
    def crossover(
        self, 
        prompt1: str, 
        prompt2: str
    ) -> str:
        """交叉两个提示词
        
        模拟遗传算法中的交叉操作
        
        Args:
            prompt1: 第一个提示
            prompt2: 第二个提示
            
        Returns:
            交叉后的新提示
        """
        # 简单策略：取前部分来自prompt1，后部分来自prompt2
        words1 = prompt1.split()
        words2 = prompt2.split()
        
        if len(words1) < 3 or len(words2) < 3:
            return prompt1
        
        # 在随机位置交叉
        split1 = random.randint(1, len(words1) - 1)
        split2 = random.randint(1, len(words2) - 1)
        
        new_words = words1[:split1] + words2[split2:]
        return " ".join(new_words)
    
    def mutate(
        self, 
        prompt: str, 
        mutation_rate: float = 0.1
    ) -> str:
        """变异提示词
        
        对提示进行随机修改
        
        Args:
            prompt: 原始提示
            mutation_rate: 变异概率
            
        Returns:
            变异后的提示
        """
        # 可能的变异操作
        mutations = [
            lambda p: "请" + p,  # 添加前缀
            lambda p: p + "。",  # 添加后缀
            lambda p: p.replace("。", "，"),  # 句式调整
            lambda p: p.replace("你", "模型"),  # 词汇替换
            lambda p: "仔细分析: " + p,  # 添加指令
        ]
        
        if random.random() < mutation_rate:
            mutation = random.choice(mutations)
            return mutation(prompt)
        
        return prompt
    
    def optimize(
        self,
        task_description: str,
        test_cases: List[Dict[str, str]],
        population_size: int = 10,
        generations: int = 5
    ) -> Dict[str, Any]:
        """提示优化主函数
        
        使用进化算法优化提示词
        
        Args:
            task_description: 任务描述
            test_cases: 测试用例
            population_size: 种群大小
            generations: 迭代代数
            
        Returns:
            优化结果
        """
        # 初始化种群
        initial_prompts = self.generate_initial_prompts(
            task_description, population_size
        )
        
        self.population = [
            PromptCandidate(prompt=p) for p in initial_prompts
        ]
        
        best_prompt = None
        best_score = 0.0
        history = []
        
        for gen in range(generations):
            # 评估所有候选
            for candidate in self.population:
                score = self.evaluate_prompt(
                    candidate.prompt, test_cases
                )
                candidate.score = score
                
                if score > best_score:
                    best_score = score
                    best_prompt = candidate.prompt
            
            history.append({
                "generation": gen,
                "best_score": best_score,
                "best_prompt": best_prompt
            })
            
            # 选择优秀个体
            sorted_pop = sorted(
                self.population, 
                key=lambda x: x.score, 
                reverse=True
            )
            elite = sorted_pop[:population_size // 2]
            
            # 生成新一代
            new_population = []
            
            # 保留精英
            new_population.extend(elite)
            
            # 交叉和变异
            while len(new_population) < population_size:
                if random.random() < 0.7 and len(elite) >= 2:
                    # 交叉
                    parent1, parent2 = random.sample(elite, 2)
                    child_prompt = self.crossover(
                        parent1.prompt, parent2.prompt
                    )
                else:
                    # 变异
                    parent = random.choice(elite)
                    child_prompt = self.mutate(parent.prompt)
                
                new_population.append(PromptCandidate(prompt=child_prompt))
            
            self.population = new_population
        
        return {
            "best_prompt": best_prompt,
            "best_score": best_score,
            "history": history
        }


# 基于聚类的提示选择
class PromptClusterSelector:
    """基于聚类的提示选择器
    
    通过聚类分析选择多样化的提示示例
    """
    
    def __init__(self, client: OpenAI, model: str = "gpt-5.4-mini"):
        self.client = client
        self.model = model
    
    def get_embedding(self, text: str) -> List[float]:
        """获取文本的embedding
        
        Args:
            text: 输入文本
            
        Returns:
            embedding向量
        """
        # 使用GPT获取文本表示（简化版）
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    
    def cluster_prompts(
        self, 
        prompts: List[str], 
        num_clusters: int = 3
    ) -> Dict[int, List[str]]:
        """对提示进行聚类
        
        Args:
            prompts: 提示列表
            num_clusters: 聚类数量
            
        Returns:
            聚类结果 {cluster_id: [prompts]}
        """
        # 获取embeddings
        embeddings = [self.get_embedding(p) for p in prompts]
        
        # 简单的聚类实现（基于余弦相似度）
        clusters = {i: [] for i in range(num_clusters)}
        cluster_centers = embeddings[:num_clusters]
        
        for i, emb in enumerate(embeddings):
            # 找最近的中心
            similarities = [
                self._cosine_similarity(emb, center) 
                for center in cluster_centers
            ]
            best_cluster = similarities.index(max(similarities))
            clusters[best_cluster].append(prompts[i])
        
        return clusters
    
    def _cosine_similarity(
        self, 
        a: List[float], 
        b: List[float]
    ) -> float:
        """计算余弦相似度"""
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        return dot_product / (norm_a * norm_b) if norm_a * norm_b > 0 else 0
    
    def select_diverse_prompts(
        self, 
        prompts: List[str], 
        num_select: int = 3
    ) -> List[str]:
        """选择多样化的提示
        
        从各聚类中选择代表性提示
        
        Args:
            prompts: 提示列表
            num_select: 选择数量
            
        Returns:
            选中的提示列表
        """
        if len(prompts) <= num_select:
            return prompts
        
        num_clusters = min(num_select, len(prompts))
        clusters = self.cluster_prompts(prompts, num_clusters)
        
        selected = []
        for cluster_id, cluster_prompts in clusters.items():
            if cluster_prompts:
                # 选择该聚类中第一个（代表）
                selected.append(cluster_prompts[0])
        
        return selected[:num_select]


# 使用示例
def ape_example():
    """APE使用示例"""
    
    task = "将以下中文句子翻译成英文"
    test_cases = [
        {"input": "你好", "expected": "Hello"},
        {"input": "今天天气真好", "expected": "The weather is nice today"},
        {"input": "我喜欢编程", "expected": "I like programming"},
    ]
    
    ape = AutomaticPromptEngineer(client=client)
    result = ape.optimize(task, test_cases, population_size=5, generations=3)
    
    print("=" * 50)
    print("Automatic Prompt Engineering 结果")
    print("=" * 50)
    print(f"最佳提示: {result['best_prompt']}")
    print(f"最佳分数: {result['best_score']:.2f}")
    
    # 聚类选择示例
    prompts = [
        "翻译下面的句子",
        "请把中文转为英文",
        "将以下内容翻译成英语",
        "你是翻译助手",
        "把句子翻译一下"
    ]
    
    selector = PromptClusterSelector(client=client)
    selected = selector.select_diverse_prompts(prompts, 3)
    print(f"\n多样选择: {selected}")
