"""
LCEL代码组织与测试最佳实践
"""

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import pytest

# ============================================================
# 推荐的项目结构
# ============================================================

"""
project/
├── chains/
│   ├── __init__.py
│   ├── qa_chain.py      # 问答链
│   ├── rag_chain.py     # RAG链
│   └── agent_chain.py   # Agent链
├── prompts/
│   ├── __init__.py
│   └── templates.py     # Prompt模板
├── tools/
│   ├── __init__.py
│   └── custom_tools.py  # 自定义工具
├── config/
│   ├── __init__.py
│   └── settings.py      # 配置
└── main.py              # 入口
"""

# ============================================================
# 模块化链定义示例
# ============================================================

# chains/qa_chain.py
def create_qa_chain(llm=None):
    """创建问答链的工厂函数"""
    
    if llm is None:
        llm = ChatOpenAI()
    
    prompt = ChatPromptTemplate.from_template(
        "你是一个知识渊博的助手。请回答以下问题：\n\n问题：{question}"
    )
    
    return (
        prompt
        | llm
        | StrOutputParser()
    )

# chains/rag_chain.py
def create_rag_chain(llm, retriever):
    """创建RAG链的工厂函数"""
    
    def format_docs(docs):
        return "\n\n".join([d.page_content for d in docs])
    
    prompt = ChatPromptTemplate.from_template(
        "基于以下上下文回答问题：\n\n上下文：{context}\n\n问题：{question}"
    )
    
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough()
        }
        | prompt
        | llm
        | StrOutputParser()
    )

# ============================================================
# 单元测试示例
# ============================================================

class TestQaChain:
    """问答链的测试类"""
    
    def test_qa_chain_structure(self):
        """测试链的结构是否正确"""
        chain = create_qa_chain()
        
        # 验证链可以调用
        assert callable(chain.invoke)
        assert callable(chain.stream)
        assert callable(chain.batch)
    
    def test_qa_chain_input_schema(self):
        """测试输入模式"""
        chain = create_qa_chain()
        schema = chain.input_schema
        
        # 应该有question字段
        assert "question" in schema.schema()["properties"]
    
    def test_qa_chain_output_schema(self):
        """测试输出模式"""
        chain = create_qa_chain()
        schema = chain.output_schema
        
        # 输出应该是字符串
        assert "str" in str(schema)
    
    @pytest.mark.asyncio
    async def test_qa_chain_async(self):
        """测试异步调用"""
        import asyncio
        chain = create_qa_chain()
        
        # 异步调用应该能正常工作
        result = await chain.ainvoke({"question": "你好"})
        assert isinstance(result, str)
        assert len(result) > 0


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
