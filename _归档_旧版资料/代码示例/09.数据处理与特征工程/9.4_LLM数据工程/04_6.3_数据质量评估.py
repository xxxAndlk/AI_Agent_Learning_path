import json                                    # JSON处理
from typing import List, Dict                  # 类型提示
from dataclasses import dataclass, field      # 数据类
import re                                      # 正则表达式

@dataclass
class QualityReport:
    """数据质量报告"""
    total_samples: int = 0                    # 总样本数
    valid_samples: int = 0                    # 有效样本数
    issues: List[Dict] = field(default_factory=list)  # 问题列表
    metrics: Dict = field(default_factory=dict)       # 质量指标


class DataQualityEvaluator:
    """数据质量评估器"""
    
    def __init__(
        self,
        min_instruction_length: int = 5,     # 指令最小长度
        max_instruction_length: int = 1000   # 指令最大长度
    ):
        """初始化评估器
        
        参数:
            min_instruction_length: 指令最小字符数
            max_instruction_length: 指令最大字符数
        """
        self.min_instruction_length = min_instruction_length
        self.max_instruction_length = max_instruction_length
    
    def evaluate_instruction_data(
        self,
        data: List[Dict]
    ) -> QualityReport:
        """评估指令数据质量
        
        参数:
            data: 指令数据列表
        返回:
            质量评估报告
        """
        report = QualityReport(total_samples=len(data))
        
        for i, sample in enumerate(data):
            issues = []                       # 当前样本的问题列表
            
            instruction = sample.get("instruction", "")
            output = sample.get("output", "")
            
            # 检查1：缺失字段
            if not instruction:
                issues.append({
                    "type": "missing_field",
                    "severity": "critical",
                    "message": f"样本 {i}: 缺少instruction字段"
                })
            
            if not output:
                issues.append({
                    "type": "missing_field",
                    "severity": "critical",
                    "message": f"样本 {i}: 缺少output字段"
                })
            
            # 检查2：长度异常
            if instruction:
                inst_len = len(instruction)
                if inst_len < self.min_instruction_length:
                    issues.append({
                        "type": "length_issue",
                        "severity": "warning",
                        "message": f"样本 {i}: 指令过短 ({inst_len}字符)"
                    })
            
            # 记录问题
            if issues:
                report.issues.extend(issues)
            else:
                report.valid_samples += 1
        
        # 计算质量分数
        valid_rate = report.valid_samples / report.total_samples if report.total_samples > 0 else 0
        report.metrics["quality_score"] = round(valid_rate * 100, 2)
        
        return report


def demonstrate_data_quality_evaluation():
    """演示数据质量评估流程"""
    
    print("=" * 60)
    print("数据质量评估演示")
    print("=" * 60)
    
    # 创建测试数据
    test_data = [
        {"instruction": "解释什么是机器学习？", "output": "机器学习是AI的一个分支。"},
        {"instruction": "什么是深度学习？", "output": ""},  # 缺少输出
        {"instruction": "翻译", "output": "你好"},           # 指令过短
    ]
    
    # 创建评估器
    evaluator = DataQualityEvaluator(min_instruction_length=5)
    
    # 评估数据
    report = evaluator.evaluate_instruction_data(test_data)
    
    print(f"\n总样本数: {report.total_samples}")
    print(f"有效样本数: {report.valid_samples}")
    print(f"质量分数: {report.metrics.get('quality_score', 0)}/100")
    
    print(f"\n发现 {len(report.issues)} 个问题:")
    for issue in report.issues:
        print(f"  [{issue['severity']}] {issue['message']}")


if __name__ == "__main__":
    demonstrate_data_quality_evaluation()
