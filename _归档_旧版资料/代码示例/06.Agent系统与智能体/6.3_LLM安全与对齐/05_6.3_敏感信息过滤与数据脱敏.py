"""
敏感信息过滤与数据脱敏

该模块提供敏感数据检测、脱敏处理和输出净化功能
支持多种敏感信息类型的识别和处理
"""

# 导入标准库
import re                                 # 正则表达式模块
import hashlib                            # 哈希函数模块
from typing import Dict, List, Tuple, Optional, Any  # 类型提示
from dataclasses import dataclass         # 数据类装饰器
from enum import Enum                      # 枚举类型


# 定义敏感级别枚举
class SensitivityLevel(Enum):
    """敏感级别枚举
    
    根据信息的敏感程度划分为四个等级
    """
    LOW = 1      # 低敏感：一般个人信息，如姓名
    MEDIUM = 2   # 中敏感：联系方式，如手机号、邮箱
    HIGH = 3     # 高敏感：重要证件，如身份证、银行卡
    CRITICAL = 4 # 极高敏感：机密凭证，如密码、API密钥


# 定义敏感信息模式数据类
@dataclass
class SensitivePattern:
    """敏感信息模式定义
    
    用于描述一种敏感信息的检测规则和处理方式
    """
    name: str           # 模式名称，用于标识
    pattern: str        # 正则表达式模式
    level: SensitivityLevel  # 敏感级别
    mask_method: str    # 脱敏方法：'hash','partial','full','redact'
    description: str    # 模式描述


class SensitiveDataFilter:
    """敏感数据过滤器类
    
    核心功能：
    - 检测文本中的敏感信息
    - 根据敏感级别进行脱敏处理
    - 提供输入安全检查
    """
    
    def __init__(self):
        """初始化敏感数据过滤器
        
        配置所有需要检测的敏感信息模式
        """
        # 初始化敏感信息模式列表
        self.patterns: List[SensitivePattern] = [
            # ===== 中国手机号 =====
            # 匹配中国大陆11位手机号，以1开头，第2位为3-9
            SensitivePattern(
                name="phone_cn",
                pattern=r'1[3-9]\d{9}',
                level=SensitivityLevel.MEDIUM,
                mask_method="partial",      # 部分掩码：显示前3位和后3位
                description="中国大陆手机号"
            ),
            
            # ===== 中国身份证号 =====
            # 匹配18位身份证号，最后一位可能是X
            SensitivePattern(
                name="id_card_cn",
                pattern=r'\d{17}[\dXx]',
                level=SensitivityLevel.HIGH,
                mask_method="partial",
                description="中国大陆身份证号"
            ),
            
            # ===== 电子邮箱 =====
            # 匹配标准邮箱格式
            SensitivePattern(
                name="email",
                pattern=r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
                level=SensitivityLevel.MEDIUM,
                mask_method="partial",
                description="电子邮件地址"
            ),
            
            # ===== 银行卡号 =====
            # 匹配16-19位数字序列
            SensitivePattern(
                name="bank_card",
                pattern=r'\d{16,19}',
                level=SensitivityLevel.HIGH,
                mask_method="partial",
                description="银行卡号"
            ),
            
            # ===== API密钥 =====
            # 匹配api_key=xxx格式，支持多种写法
            SensitivePattern(
                name="api_key",
                pattern=r'(?:api[_-]?key|apikey)[\s]*[=:]+[\s]*["\']?[a-zA-Z0-9]{16,}["\']?',
                level=SensitivityLevel.CRITICAL,
                mask_method="full",         # 完全掩码
                description="API密钥"
            ),
            
            # ===== 密码 =====
            # 匹配password=xxx格式
            SensitivePattern(
                name="password",
                pattern=r'(?:password|passwd|pwd)[\s]*[=:]+[\s]*["\']?[^"\'\s]+["\']?',
                level=SensitivityLevel.CRITICAL,
                mask_method="full",
                description="密码"
            ),
            
            # ===== 姓名（中文） =====
            # 匹配"姓名：张三"格式
            SensitivePattern(
                name="name_cn",
                pattern=r'[姓|名][名|称]?[\s]*[:：][\s]*([\u4e00-\u9fa5]{2,4})',
                level=SensitivityLevel.LOW,
                mask_method="hash",         # 哈希处理
                description="中文姓名"
            ),
        ]
        
        # 初始化检测日志
        self.detection_log: List[Dict] = []
    
    def detect_sensitive_data(self, text: str) -> List[Dict]:
        """检测敏感信息
        
        扫描文本，识别所有匹配的敏感信息
        参数:
            text: 待检测的文本
        返回:
            检测结果列表，每个结果包含类型、值、位置等信息
        """
        # 存储检测结果
        findings = []
        
        # 遍历所有敏感模式
        for pattern in self.patterns:
            # 使用正则查找所有匹配项
            # re.IGNORECASE使匹配不区分大小写
            matches = re.finditer(pattern.pattern, text, re.IGNORECASE)
            
            # 处理每个匹配项
            for match in matches:
                # 创建发现记录
                finding = {
                    "type": pattern.name,           # 模式名称
                    "value": match.group(),         # 匹配的原始文本
                    "position": (match.start(), match.end()),  # 在文本中的位置
                    "level": pattern.level.name,    # 敏感级别名称
                    "description": pattern.description,  # 描述
                    "mask_method": pattern.mask_method   # 脱敏方法
                }
                findings.append(finding)
        
        # ===== 记录检测日志 =====
        # 保存检测结果用于审计和分析
        self.detection_log.append({
            "text_sample": text[:100] + "..." if len(text) > 100 else text,  # 文本样本
            "findings_count": len(findings),  # 发现数量
            # 统计高风险发现数量
            "high_risk_count": sum(1 for f in findings if f["level"] in ["HIGH", "CRITICAL"])
        })
        
        return findings
    
    def mask_sensitive_data(
        self, 
        text: str, 
        findings: Optional[List[Dict]] = None
    ) -> str:
        """脱敏处理
        
        根据检测结果对敏感信息进行脱敏
        参数:
            text: 原始文本
            findings: 预计算的检测结果，可选
        返回:
            脱敏后的文本
        """
        # 如果未提供检测结果，先执行检测
        if findings is None:
            findings = self.detect_sensitive_data(text)
        
        # ===== 排序处理 =====
        # 按位置从后向前排序，避免替换时位置偏移问题
        # 反向排序确保先处理后面的内容，不会影响前面的位置
        sorted_findings = sorted(findings, key=lambda x: x["position"][0], reverse=True)
        
        # 从原始文本开始，依次替换
        masked_text = text
        
        # 遍历每个发现进行处理
        for finding in sorted_findings:
            # 获取位置和原始值
            start, end = finding["position"]
            original = finding["value"]
            # 获取脱敏方法
            mask_method = finding.get("mask_method", "redact")
            
            # ===== 根据脱敏方法进行处理 =====
            if mask_method == "hash":
                # 哈希方法：使用SHA256生成哈希值
                # 取前8位作为短标识
                replacement = hashlib.sha256(original.encode()).hexdigest()[:8]
                
            elif mask_method == "partial":
                # 部分掩码：保留首尾部分字符
                # 例如：138****8000
                if len(original) > 8:  # 长度大于8才进行部分掩码
                    replacement = original[:3] + "****" + original[-3:]
                else:
                    replacement = "****"  # 长度不足则完全掩码
                    
            elif mask_method == "full":
                # 完全掩码：直接替换为标记
                replacement = "[REDACTED]"
                
            else:  # "redact"
                # 默认脱敏：通用标记
                replacement = "[SENSITIVE_DATA]"
            
            # ===== 执行替换 =====
            # 使用字符串切片进行替换
            masked_text = masked_text[:start] + replacement + masked_text[end:]
        
        return masked_text
    
    def check_input_safety(self, text: str) -> Dict[str, Any]:
        """检查输入安全性
        
        综合评估文本的安全风险
        参数:
            text: 待检查的文本
        返回:
            安全检查结果
        """
        # 执行敏感信息检测
        findings = self.detect_sensitive_data(text)
        
        # ===== 统计各级别数量 =====
        level_counts = {}
        for finding in findings:
            level = finding["level"]
            level_counts[level] = level_counts.get(level, 0) + 1
        
        # ===== 判断风险等级 =====
        # CRITICAL级别：绝对不允许
        if level_counts.get("CRITICAL", 0) > 0:
            risk_level = "CRITICAL"
            allowed = False
            
        # HIGH级别：也不允许
        elif level_counts.get("HIGH", 0) > 0:
            risk_level = "HIGH"
            allowed = False
            
        # 超过5处敏感信息：中等风险
        elif sum(level_counts.values()) > 5:
            risk_level = "MEDIUM"
            allowed = True
            
        # 其他情况：低风险
        else:
            risk_level = "LOW"
            allowed = True
        
        # ===== 准备返回结果 =====
        return {
            "allowed": allowed,                          # 是否允许通过
            "risk_level": risk_level,                    # 风险等级
            "findings": findings,                        # 发现列表
            "level_counts": level_counts,                # 各级别统计
            # 如果不允许，生成脱敏文本；否则返回原文本
            "masked_text": self.mask_sensitive_data(text, findings) if not allowed else text
        }


class OutputSanitizer:
    """输出净化器类
    
    用于处理AI系统输出中的敏感信息
    在内容返回给用户前进行最后一层过滤
    """
    
    def __init__(self):
        """初始化输出净化器"""
        # 初始化敏感数据过滤器
        self.filter = SensitiveDataFilter()
        
        # ===== 定义输出审查规则 =====
        # 禁止在输出中出现以下内容
        self.forbidden_patterns = [
            # 凭证信息：password、api_key、secret等
            r'(?:password|api.?key|secret)["\']?\s*[:=]\s*["\']?\S+["\']?',
            # 长数字序列：可能是银行卡号等
            r'\b\d{16,19}\b',
            # 内部/机密信息标记
            r'(?:internal|confidential|classified).{0,20}(?:document|file|info)',
        ]
    
    def sanitize_output(
        self, 
        text: str, 
        user_clearance: str = "low"
    ) -> Dict[str, Any]:
        """净化输出
        
        对AI生成的输出进行处理
        参数:
            text: 原始输出文本
            user_clearance: 用户权限级别："low"、"medium"、"high"
        返回:
            净化结果
        """
        # 初始化结果
        result = {
            "original": text,       # 原始输出
            "sanitized": text,      # 净化后输出（初始为原始）
            "modifications": [],    # 修改记录
            "blocked": False        # 是否完全阻止
        }
        
        # ===== 步骤1：检测敏感信息 =====
        # 使用过滤器检查输出
        safety_check = self.filter.check_input_safety(text)
        
        # 如果检测到高风险内容，进行脱敏
        if safety_check["risk_level"] in ["CRITICAL", "HIGH"]:
            result["sanitized"] = safety_check["masked_text"]
            result["modifications"].append("敏感信息脱敏")
        
        # ===== 步骤2：检查禁止内容 =====
        # 遍历所有禁止模式
        for pattern in self.forbidden_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result["blocked"] = True
                result["modifications"].append("包含禁止披露的信息")
                break  # 发现一项禁止内容即可
        
        # ===== 步骤3：基于权限过滤 =====
        # 根据用户权限级别进行额外处理
        if user_clearance == "low":
            # 低权限用户：隐藏代码块
            # 使用正则替换所有代码块
            result["sanitized"] = re.sub(r'```[\s\S]*?```', '[代码已隐藏]', result["sanitized"])
        
        return result


# ============ 使用示例函数 ============

def sensitive_data_example():
    """敏感信息处理示例
    
    演示敏感信息检测、脱敏和安全检查的使用
    """
    
    print("="*60)
    print("敏感信息过滤与脱敏")
    print("="*60)
    
    # 创建过滤器实例
    filter_tool = SensitiveDataFilter()
    
    # 测试用例列表
    test_cases = [
        "我的手机号是13800138000，请帮我查询",
        "身份证号：110101199001011234",
        "API Key: sk-abc123def456ghi789",
        "邮箱地址：user@example.com",
        "密码: mySecretPassword123"
    ]
    
    # 遍历测试每种类型
    for text in test_cases:
        print(f"\n原始: {text}")
        
        # 检测敏感信息
        findings = filter_tool.detect_sensitive_data(text)
        if findings:
            print(f"检测到 {len(findings)} 处敏感信息:")
            for f in findings:
                # 显示级别和描述，截断显示值
                print(f"  - [{f['level']}] {f['description']}: {f['value'][:20]}...")
        
        # 执行脱敏
        masked = filter_tool.mask_sensitive_data(text)
        print(f"脱敏: {masked}")
    
    # ===== 综合安全检查示例 =====
    print("\n" + "="*60)
    print("综合安全检查示例")
    print("="*60)
    
    # 复杂输入测试
    complex_input = """
    用户信息：
    姓名：张三
    手机号：13800138000
    邮箱：zhangsan@example.com
    API配置：api_key=sk-secret123456789
    """
    
    # 执行安全检查
    safety = filter_tool.check_input_safety(complex_input)
    print(f"\n风险等级: {safety['risk_level']}")
    print(f"是否允许: {safety['allowed']}")
    print(f"敏感信息统计: {safety['level_counts']}")
    print(f"\n脱敏后文本:\n{safety['masked_text']}")
    
    # ===== 输出净化示例 =====
    print("\n" + "="*60)
    print("输出净化示例")
    print("="*60)
    
    # 创建净化器
    sanitizer = OutputSanitizer()
    
    # 模拟AI输出
    ai_output = """
    根据您的请求，我找到了以下信息：
    用户手机号：13800138000
    数据库密码：db_secret_2024
    API密钥：sk-live-abcdef123456
    """
    
    # 净化输出
    sanitized = sanitizer.sanitize_output(ai_output, user_clearance="low")
    print(f"\n原始输出:\n{ai_output}")
    print(f"净化后:\n{sanitized['sanitized']}")
    print(f"修改记录: {sanitized['modifications']}")


# ===== 程序入口 =====
if __name__ == "__main__":
    # 运行示例
    sensitive_data_example()
