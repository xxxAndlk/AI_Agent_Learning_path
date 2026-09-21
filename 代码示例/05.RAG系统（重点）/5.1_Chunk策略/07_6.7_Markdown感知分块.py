# Markdown感知分块专门处理Markdown格式的文档
# 保留Markdown的标题、代码块等结构信息

from langchain_text_splitters import MarkdownTextSplitter, RecursiveCharacterTextSplitter

# 示例Markdown文档
markdown_content = """
# Python编程指南

## 简介

Python是一种高级编程语言，由Guido van Rossum于1991年创建。
Python的设计哲学强调代码的可读性和简洁的语法。

## 基本语法

### 变量和数据类型

Python使用动态类型系统，不需要显式声明变量类型。

```python
# 整数
age = 25

# 浮点数
price = 19.99

# 字符串
name = "Alice"

# 列表
numbers = [1, 2, 3, 4, 5]

# 字典
person = {"name": "Bob", "age": 30}
```

### 控制流

```python
# 条件语句
if age >= 18:
    print("成年人")
else:
    print("未成年人")

# 循环
for i in range(5):
    print(i)

# 列表推导式
squares = [x**2 for x in range(10)]
```

## 函数

定义函数的语法如下：

```python
def greet(name, greeting="Hello"):
    \"\"\"问候函数\"\"\"
    return f"{greeting}, {name}!"

# 调用函数
result = greet("Alice")
print(result)  # 输出: Hello, Alice!
```

### 参数类型

Python支持多种参数类型：

- 位置参数
- 关键字参数
- 默认参数
- *args和**kwargs

## 面向对象编程

### 类定义

```python
class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        return f"Hello, I'm {self.name}"
```

## 总结

Python是一门功能强大且易于学习的编程语言，适合各种开发场景。

"""

# 方法1：使用MarkdownTextSplitter
# MarkdownTextSplitter会识别Markdown语法结构，按标题层级分块
# 内置按标题层级与代码块边界切分的分隔符

markdown_splitter = MarkdownTextSplitter(
    chunk_size=300,           # 每个块最大300字符
    chunk_overlap=50,         # 重叠50字符
)

markdown_chunks = markdown_splitter.split_text(markdown_content)

print(f"Markdown感知分块结果：共 {len(markdown_chunks)} 个块\n")

for i, chunk in enumerate(markdown_chunks):
    # 检测chunk中是否包含代码块
    has_code = "```" in chunk
    code_indicator = " [含代码]" if has_code else ""
    
    print(f"[块{i+1}] {len(chunk)}字符{code_indicator}")
    # 只显示前80个字符
    preview = chunk[:80].replace("\n", " ")
    print(f"预览: {preview}...")
    print()
```

---

### 6.8 代码感知分块

```python
# 代码感知分块专门处理代码文档
# 保持代码的完整性，不在语句中间截断

from langchain_text_splitters import Language, RecursiveCharacterTextSplitter
import re

# 示例代码文件
code_content = """
def fibonacci(n):
    \"\"\"计算斐波那契数列的第n项
    
    参数:
        n: 要计算的项数（从0开始）
    
    返回:
        斐波那契数列的第n项
    \"\"\"
    if n <= 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n-1) + fibonacci(n-2)

class DataProcessor:
    \"\"\"数据处理器类\"\"\"
    
    def __init__(self, data):
        \"\"\"初始化处理器
        
        参数:
            data: 初始数据列表
        \"\"\"
        self.data = data
        self.processed = False
    
    def process(self):
        \"\"\"处理数据\"\"\"
        self.data = [x * 2 for x in self.data]
        self.processed = True
        return self.data
    
    def get_statistics(self):
        \"\"\"获取数据统计信息\"\"\"
        if not self.processed:
            self.process()
        
        return {
            'sum': sum(self.data),
            'mean': sum(self.data) / len(self.data),
            'min': min(self.data),
            'max': max(self.data)
        }

# 主程序
if __name__ == "__main__":
    processor = DataProcessor([1, 2, 3, 4, 5])
    stats = processor.get_statistics()
    print(f"统计结果: {stats}")
"""

# 方法1：使用RecursiveCharacterTextSplitter.from_language
# 针对不同编程语言使用对应的分隔符

# 支持的语言包括：Python, JavaScript, Java, C++, Go, Ruby等
code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,  # 指定Python语言
    chunk_size=200,            # 每个块最大200字符
    chunk_overlap=30,          # 重叠30字符
)

code_chunks = code_splitter.split_text(code_content)

print(f"代码感知分块结果（Python）：共 {len(code_chunks)} 个块\n")

for i, chunk in enumerate(code_chunks):
    print(f"--- 块 {i+1} ({len(chunk)}字符) ---")
    print(chunk)
    print()


# 方法2：自定义代码分块器
# 针对特定需求可以自定义分块策略

def custom_code_splitter(text, language="python"):
    """自定义代码分块器，保持函数和类的完整性"""
    
    if language == "python":
        # Python的分隔符优先级
        separators = [
            "\nclass ",       # 类定义
            "\ndef ",         # 函数定义
            "\n    ",         # 缩进块（函数/类内部）
            "\n",             # 行
            " ",              # 空格
            ""                # 字符
        ]
    else:
        separators = ["\n", " ", ""]
    
    # 使用递归分块器
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=separators,
        keep_separator=True,
    )
    
    return splitter.split_text(text)

# 测试自定义分块器
custom_chunks = custom_code_splitter(code_content, "python")

print(f"自定义代码分块结果：共 {len(custom_chunks)} 个块\n")

for i, chunk in enumerate(custom_chunks):
    print(f"[块{i+1}] {len(chunk)}字符")
    preview = chunk[:100].replace("\n", " | ")
    print(f"  {preview}...")
```

---

### 6.9 多模态分块

```python
# 多模态分块处理包含文本、图像、表格等多种内容类型的文档
# 需要使用专门的文档加载器提取不同模态的内容

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader, UnstructuredImageLoader
from langchain_core.documents import Document
import base64
from io import BytesIO
from PIL import Image

# 模拟多模态文档处理
# 实际应用中需要根据文档类型选择合适的加载器

class MultimodalChunker:
    """多模态文档分块器，处理文本、图像、表格等内容"""
    
    def __init__(self, chunk_size=500, chunk_overlap=50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", "。", "！", "？", "；", ""]
        )
    
    def chunk_text(self, text):
        """纯文本分块"""
        return self.text_splitter.split_text(text)
    
    def chunk_with_image_context(self, text, image_descriptions):
        """
        带图像上下文的分块
        图像描述可以作为Chunk的元数据
        
        参数:
            text: 文本内容
            image_descriptions: 图像描述列表
        
        返回:
            带有图像上下文的文档块列表
        """
        text_chunks = self.text_splitter.split_text(text)
        documents = []
        
        for i, chunk in enumerate(text_chunks):
            # 查找与当前文本块相关的图像
            related_images = []
            for img_desc in image_descriptions:
                # 简单判断：图像是否在当前块附近
                if img_desc.get("position", 0) in range(
                    i * self.chunk_size, 
                    (i + 1) * self.chunk_size
                ):
                    related_images.append(img_desc)
            
            # 创建Document对象
            doc = Document(
                page_content=chunk,
                metadata={
                    "chunk_index": i,
                    "related_images": related_images,
                    "has_images": len(related_images) > 0
                }
            )
            documents.append(doc)
        
        return documents
    
    def chunk_table(self, table_data):
        """
        表格分块
        可以按行或按列分块，保留表头
        """
        if not table_data or "headers" not in table_data:
            return []
        
        headers = table_data["headers"]
        rows = table_data.get("rows", [])
        chunks = []
        
        # 策略1：整表作为一个块（如果不太大）
        if len(str(headers)) + sum(len(str(row)) for row in rows) < self.chunk_size:
            table_text = self._format_table(headers, rows)
            chunks.append(Document(
                page_content=table_text,
                metadata={"type": "table", "row_count": len(rows)}
            ))
        else:
            # 策略2：分多行存储，保持表头重复
            current_rows = []
            current_size = len(str(headers))
            
            for row in rows:
                row_size = len(str(row))
                if current_size + row_size > self.chunk_size and current_rows:
                    # 保存当前块
                    table_text = self._format_table(headers, current_rows)
                    chunks.append(Document(
                        page_content=table_text,
                        metadata={"type": "table", "row_count": len(current_rows)}
                    ))
                    current_rows = [row]
                    current_size = row_size
                else:
                    current_rows.append(row)
                    current_size += row_size
            
            # 保存最后一个块
            if current_rows:
                table_text = self._format_table(headers, current_rows)
                chunks.append(Document(
                    page_content=table_text,
                    metadata={"type": "table", "row_count": len(current_rows)}
                ))
        
        return chunks
    
    def _format_table(self, headers, rows):
        """格式化表格为文本"""
        lines = [",".join(str(h) for h in headers)]
        for row in rows:
            lines.append(",".join(str(cell) for cell in row))
        return "\n".join(lines)


# 演示多模态分块
print("=== 多模态分块演示 ===\n")

# 创建多模态分块器
multi_chunker = MultimodalChunker(chunk_size=300, chunk_overlap=30)

# 测试文本分块
sample_text = """
本文介绍了一款新型智能手机的设计特点。该手机采用6.7英寸AMOLED显示屏，
分辨率为3216x1440像素，支持120Hz刷新率。处理器采用最新的骁龙8系列芯片，
性能相比上一代提升30%。电池容量为5000mAh，支持65W快充。

手机背面配备了三个摄像头：主摄为1亿像素，支持光学防抖；
超广角镜头为1200万像素，视角达到120度；长焦镜头为800万像素，
支持3倍光学变焦。相机系统还支持AI场景识别和夜景模式。
"""

text_chunks = multi_chunker.chunk_text(sample_text)
print(f"文本分块结果：共 {len(text_chunks)} 个块\n")

for i, chunk in enumerate(text_chunks):
    print(f"[文本块{i+1}] {chunk[:80]}...")

# 测试表格分块
sample_table = {
    "headers": ["型号", "屏幕", "处理器", "电池", "价格"],
    "rows": [
        ["Phone A", "6.1英寸", "骁龙8", "4000mAh", "5999元"],
        ["Phone B", "6.7英寸", "骁龙8+", "5000mAh", "6999元"],
        ["Phone C", "6.9英寸", "骁龙8 Gen2", "6000mAh", "7999元"],
    ]
}

table_chunks = multi_chunker.chunk_table(sample_table)
print(f"\n表格分块结果：共 {len(table_chunks)} 个块\n")

for i, chunk in enumerate(table_chunks):
    print(f"[表格块{i+1}]")
    print(chunk.page_content)
    print(f"元数据: {chunk.metadata}")
```

---

### 6.10 分块质量评估

```python
# 分块质量评估工具
# 用于评估分块效果，指导参数调优

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
import numpy as np
from collections import Counter

class ChunkQualityEvaluator:
    """分块质量评估器"""
    
    def __init__(self, embeddings_model=None):
        """
        初始化评估器
        
        参数:
            embeddings_model: 用于计算语义的embedding模型
        """
        if embeddings_model is None:
            try:
                self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            except:
                self.embeddings = None
                print("警告：未找到embedding模型，将跳过语义评估")
        else:
            self.embeddings = embeddings_model
    
    def evaluate_chunks(self, chunks, original_text):
        """
        评估分块质量
        
        参数:
            chunks: 分块后的文本列表
            original_text: 原始文本
        
        返回:
            评估结果字典
        """
        results = {
            "chunk_count": len(chunks),
            "avg_chunk_size": np.mean([len(c) if isinstance(c, str) else len(c.page_content) for c in chunks]),
            "size_std": np.std([len(c) if isinstance(c, str) else len(c.page_content) for c in chunks]),
            "min_chunk_size": min([len(c) if isinstance(c, str) else len(c.page_content) for c in chunks]),
            "max_chunk_size": max([len(c) if isinstance(c, str) else len(c.page_content) for c in chunks]),
            "coverage": self._calculate_coverage(chunks, original_text),
            "overlap_rate": self._calculate_overlap_rate(chunks),
        }
        
        # 语义评估（如果可用）
        if self.embeddings:
            results["semantic_coherence"] = self._calculate_semantic_coherence(chunks)
        
        return results
    
    def _calculate_coverage(self, chunks, original_text):
        """计算文本覆盖率"""
        # 将所有chunk拼接，看覆盖了多少原始文本
        combined = "".join([c if isinstance(c, str) else c.page_content for c in chunks])
        
        # 简单的覆盖率计算
        original_len = len(original_text)
        covered = len(combined)
        
        # 考虑重叠部分
        overlap = covered - original_len
        if overlap > 0:
            coverage = 100.0
        else:
            coverage = (covered / original_len) * 100 if original_len > 0 else 0
        
        return coverage
    
    def _calculate_overlap_rate(self, chunks):
        """计算重叠率"""
        if len(chunks) < 2:
            return 0.0
        
        total_chars = sum(len(c) if isinstance(c, str) else len(c.page_content) for c in chunks)
        overlap_chars = 0
        
        # 简化计算：假设每个块平均重叠10-20%
        # 实际应该根据具体分割算法计算
        avg_overlap = total_chars * 0.1  # 假设10%重叠
        overlap_rate = (avg_overlap / total_chars) * 100 if total_chars > 0 else 0
        
        return overlap_rate
    
    def _calculate_semantic_coherence(self, chunks):
        """计算语义连贯性"""
        if not self.embeddings or len(chunks) < 2:
            return None
        
        try:
            # 将chunk转换为向量
            texts = [c if isinstance(c, str) else c.page_content for c in chunks]
            embeddings = self.embeddings.embed_documents(texts)
            
            # 计算相邻chunk之间的余弦相似度
            coherences = []
            for i in range(len(embeddings) - 1):
                sim = self._cosine_similarity(embeddings[i], embeddings[i+1])
                coherences.append(sim)
            
            return np.mean(coherences) if coherences else None
        except Exception as e:
            print(f"语义连贯性计算失败: {e}")
            return None
    
    def _cosine_similarity(self, vec1, vec2):
        """计算余弦相似度"""
        dot = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot / (norm1 * norm2)
    
    def print_evaluation_report(self, results):
        """打印评估报告"""
        print("=" * 50)
        print("分块质量评估报告")
        print("=" * 50)
        print(f"分块数量: {results['chunk_count']}")
        print(f"平均块大小: {results['avg_chunk_size']:.1f} 字符")
        print(f"大小标准差: {results['size_std']:.1f}")
        print(f"最小块: {results['min_chunk_size']} 字符")
        print(f"最大块: {results['max_chunk_size']} 字符")
        print(f"文本覆盖率: {results['coverage']:.1f}%")
        print(f"重叠率: {results['overlap_rate']:.1f}%")
        
        if results.get('semantic_coherence') is not None:
            print(f"语义连贯性: {results['semantic_coherence']:.3f}")
        
        print("=" * 50)


# 演示分块质量评估
print("=== 分块质量评估演示 ===\n")

# 示例文档
sample_doc = """
机器学习是人工智能的核心技术，受到广泛关注。机器学习算法可以从数据中
自动学习规律，并进行预测和决策。监督学习、无监督学习和强化学习是
机器学习的三大类别。

深度学习是机器学习的分支，使用多层神经网络。卷积神经网络在计算机视觉
领域取得巨大成功。循环神经网络适合处理序列数据。Transformer架构
近年来在自然语言处理领域占据主导地位。

计算机视觉让机器看懂世界。图像分类、目标检测、语义分割是经典任务。
预训练模型大幅提升了视觉任务的性能。迁移学习使得小数据集也能训练
有效模型。

自然语言处理研究如何让机器理解人类语言。词向量技术将词语映射到向量空间。
注意力机制让模型关注关键信息。BERT和GPT系列模型推动了NLP的发展。
"""

# 测试不同的分块参数
test_configs = [
    {"chunk_size": 100, "chunk_overlap": 20},
    {"chunk_size": 200, "chunk_overlap": 40},
    {"chunk_size": 300, "chunk_overlap": 50},
]

evaluator = ChunkQualityEvaluator()

for config in test_configs:
    print(f"\n配置: chunk_size={config['chunk_size']}, overlap={config['chunk_overlap']}")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=["\n\n", "\n", "。", "；", "，", ""]
    )
    
    chunks = splitter.split_text(sample_doc)
    results = evaluator.evaluate_chunks(chunks, sample_doc)
    evaluator.print_evaluation_report(results)
````

---

## 7 Chunk大小选择指南

### 7.1 影响因素

选择合适的chunk_size需要考虑多个因素：

**文档因素**：
- 文档的平均长度和结构
- 主题的集中程度
- 是否包含代码、表格等特殊内容

**应用因素**：
- 使用的embedding模型的上下文窗口
- 大语言模型的上下文窗口限制
- 检索系统的延迟要求

**质量因素**：
- 召回率要求（是否允许遗漏相关信息）
- 准确率要求（是否允许包含过多无关内容）
- 上下文连贯性要求

### 7.2 常见场景推荐值

| 场景 | 推荐chunk_size | 推荐overlap | 说明 |
|------|----------------|-------------|------|
| 通用文档 | 300-500字符 | 50-100字符 | 平衡效果和性能 |
| 问答系统 | 200-400字符 | 40-80字符 | 确保问题和答案在同块 |
| 代码检索 | 500-1000字符 | 50-100字符 | 保持代码完整性 |
| 简短FAQ | 100-200字符 | 20-40字符 | 每个问题单独成块 |
| 长文档摘要 | 500-800字符 | 100-150字符 | 保留更多上下文 |

### 7.3 调优方法

1. **网格搜索**：尝试不同的chunk_size和overlap组合
2. **A/B测试**：在真实查询上测试不同配置的效果
3. **质量评估**：使用上述评估工具量化效果
4. **人工审查**：抽样检查分块结果是否合理

---

## 8 常见问题

### 8.1 Chunk大小如何选择

**问题**：如何确定最佳的chunk_size参数？

**解答**：
- 通用场景：100-500字符是较好的起始范围
- 问答系统：通常200-500字符效果较好
- 代码检索：可以稍大，保留完整代码片段
- 需要根据实际效果调优，观察检索召回率和准确率

### 8.2 如何处理不同文档格式

**问题**：如何处理PDF、Word等非纯文本格式？

**解答**：
- 使用LangChain提供的专门加载器（如PyPDFLoader、Docx2txtLoader）
- 或者先将文档转换为纯文本再进行分块
- 表格内容需要特殊处理，可能需要按行或按单元格分块

### 8.3 重叠区域大小设置

**问题**：chunk_overlap设置多大合适？

**解答**：
- 过小：可能丢失关键上下文信息
- 过大：导致块之间重复内容过多，增加存储和计算成本
- 通常设置为chunk_size的10-20%，如chunk_size=100时，overlap=20

### 8.4 语义分块效果不稳定

**问题**：语义分块的结果不稳定，有时分割过细有时过粗

**解答**：
- 调整相似度阈值：阈值越低，分割越粗；阈值越高，分割越细
- 使用百分位策略：根据数据集中相似度分布的百分位来设置阈值
- 对关键文档可以先进行人工标注，再微调阈值

---

## 9 应用场景

### 9.1 企业知识库问答

**场景**：企业员工通过问答系统查询内部文档、政策、流程等信息。

**Chunk策略选择**：
- 使用递归分块，保持文档结构的完整性
- chunk_size设为300-500字符
- chunk_overlap设为50-100字符
- 对重要文档可以适当增大chunk_size以保留更多上下文

### 9.2 技术文档检索

**场景**：开发者检索API文档、代码示例、技术教程等。

**Chunk策略选择**：
- 代码片段应保持完整性，不应在代码中间截断
- 可以使用自定义分隔符，确保在代码块边界分割
- 对长代码可以考虑按函数/类级别分割

### 9.3 客服机器人

**场景**：电商或服务行业使用AI客服回答用户问题。

**Chunk策略选择**：
- FAQ类文档可以设置较小的chunk_size（100-200字符）
- 对产品说明文档可以适当增大
- 注意保留问题与答案的完整性

### 9.4 学术论文检索

**场景**：研究人员在学术数据库中检索论文、专利等。

**Chunk策略选择**：
- 摘要和引言可以设置较小chunk
- 全文使用较大chunk或按章节分割
- 注意保留图表标题和参考文献的关联

### 9.5 法律文档分析

**场景**：律师事务所或企业法务检索法律条文、判例等。

**Chunk策略选择**：
- 法律条文应保持条款完整性，按"第X条"分割
- 判例分析可以按段落分割
- 注意保留条款之间的引用关系

---

## 10 高级技巧

### 10.1 混合分块策略

对于复杂的文档，可以采用混合策略：
- 先按文档结构（章节、段落）初步分块
- 对不同类型的Content应用不同的分块器
- 最后对过大的块进行二次分割

### 10.2 层级分块

创建多个粒度的chunk：
- 细粒度：100-200字符，用于精确检索
- 中粒度：300-500字符，用于一般问答
- 粗粒度：800-1000字符，用于需要更多上下文的场景

检索时可以根据查询类型选择不同粒度的chunk。

### 10.3 动态chunk_size

根据文档特征动态调整chunk_size：
- 简单文档：使用较大的chunk_size
- 复杂文档：使用较小的chunk_size
- 代码密集型文档：使用代码感知分块

---

**总结**

Chunk策略是RAG系统的基础环节，直接影响检索和生成效果。选择合适的分块方法需要综合考虑文档特点、应用场景和性能要求。在实际应用中，建议先使用默认参数进行测试，再根据具体效果进行调优。本文档详细介绍了10种不同的分块策略，开发者可以根据实际需求选择最适合的方法，也可以组合使用多种策略以达到最佳效果。

> 更新时间：2026年9月
