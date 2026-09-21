import openai
from typing import List, Dict, Any
import json
from dataclasses import dataclass
from enum import Enum

class EvaluationMetric(Enum):
    """评测指标类型"""
    ACCURACY = "accuracy"           # 准确率
    BLEU = "bleu"                   # BLEU分数
    ROUGE = "rouge"                 # ROUGE分数
    COSINE_SIMILARITY = "cosine"    # 余弦相似度
    EXACT_MATCH = "exact_match"     # 精确匹配

@dataclass
class BenchmarkCase:
    """评测用例"""
    input: str                      # 输入
    expected_output: str            # 期望输出
    category: str                   # 类别
    difficulty: str = "medium"      # 难度

@dataclass
class EvaluationResult:
    """评测结果"""
    metric: EvaluationMetric
    score: float
    details: Dict[str, Any]

class LLMBenchmark:
    """LLM基准评测器
    
    对LLM进行标准化能力评测
    """
    
    def __init__(self, model_name: str = "gpt-5.4"):
        self.model_name = model_name
        self.client = openai.OpenAI()
        self.results: List[EvaluationResult] = []
    
    def evaluate_accuracy(self, test_cases: List[BenchmarkCase]) -> EvaluationResult:
        """评测准确率"""
        correct = 0
        total = len(test_cases)
        
        for case in test_cases:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": case.input}]
            )
            predicted = response.choices[0].message.content.strip()
            
            # 简单精确匹配（实际可用更复杂的相似度计算）
            if predicted.lower() == case.expected_output.lower():
                correct += 1
        
        accuracy = correct / total if total > 0 else 0
        
        return EvaluationResult(
            metric=EvaluationMetric.ACCURACY,
            score=accuracy,
            details={"correct": correct, "total": total}
        )
    
    def evaluate_code_generation(self, code_cases: List[BenchmarkCase]) -> EvaluationResult:
        """评测代码生成能力"""
        passed = 0
        total = len(code_cases)
        
        for case in code_cases:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": case.input}]
            )
            code = response.choices[0].message.content
            
            # 提取代码块
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0]
            
            # 执行测试（简化版，实际应使用sandbox）
            try:
                exec(code)
                passed += 1
            except:
                pass
        
        pass_rate = passed / total if total > 0 else 0
        
        return EvaluationResult(
            metric=EvaluationMetric.EXACT_MATCH,
            score=pass_rate,
            details={"passed": passed, "total": total}
        )
    
    def run_full_benchmark(self, benchmark_suite: Dict[str, List[BenchmarkCase]]) -> Dict[str, Any]:
        """运行完整评测套件"""
        results = {}
        
        for category, cases in benchmark_suite.items():
            print(f"\n[评测] {category}: {len(cases)} 个用例")
            
            if category in ["knowledge_qa", "reasoning"]:
                result = self.evaluate_accuracy(cases)
            elif category == "code_generation":
                result = self.evaluate_code_generation(cases)
            else:
                result = self.evaluate_accuracy(cases)
            
            results[category] = {
                "metric": result.metric.value,
                "score": result.score,
                "details": result.details
            }
            
            print(f"  得分: {result.score:.2%}")
        
        # 计算总分
        avg_score = sum(r["score"] for r in results.values()) / len(results)
        results["overall"] = {"score": avg_score}
        
        return results


# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建评测套件
    benchmark_suite = {
        "knowledge_qa": [
            BenchmarkCase(
                input="法国的首都是哪里？",
                expected_output="巴黎",
                category="geography",
                difficulty="easy"
            ),
            BenchmarkCase(
                input="爱因斯坦提出了什么著名理论？",
                expected_output="相对论",
                category="science",
                difficulty="easy"
            )
        ],
        "reasoning": [
            BenchmarkCase(
                input="如果所有的A都是B，所有的B都是C，那么A和C的关系是什么？",
                expected_output="所有的A都是C",
                category="logic",
                difficulty="medium"
            )
        ],
        "code_generation": [
            BenchmarkCase(
                input="写一个Python函数计算斐波那契数列的第n项",
                expected_output="",
                category="algorithm"
            )
        ]
    }
    
    # 运行评测
    evaluator = LLMBenchmark(model_name="gpt-5.4")
    results = evaluator.run_full_benchmark(benchmark_suite)
    
    print("\n" + "="*50)
    print("评测完成!")
    print(f"总体得分: {results['overall']['score']:.2%}")
    print("="*50)
