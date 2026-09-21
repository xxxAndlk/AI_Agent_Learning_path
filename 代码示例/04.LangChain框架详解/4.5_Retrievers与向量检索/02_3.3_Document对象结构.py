from langchain_core.documents import Document

# Document结构
doc = Document(
    page_content="这是文档的实际内容...",  # 文档文本内容
    metadata={                               # 元数据
        "source": "document.txt",            # 来源文件
        "page": 1,                           # 页码
        "author": "张三",                     # 作者
        "timestamp": "2024-01-01",           # 时间戳
        "custom_field": "自定义值"            # 自定义字段
    }
)

# 访问文档内容
print(doc.page_content)  # 获取文本内容
print(doc.metadata)      # 获取元数据
print(doc.metadata.get("source"))  # 获取特定元数据
