"""
传统Chain与LCEL的详细对比示例
本示例展示了两种方式的代码量和灵活性差异
"""

# 传统方式（v0.x 旧范式，v1.x 已迁移至 langchain-classic，仅作迁移对照）
# from langchain.chains import LLMChain, RetrievalQA
# from langchain.chains.combine_documents import stuff
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 步骤1：创建第一个Chain用于生成问题
prompt1 = PromptTemplate(
    template="把以下内容转换成3个问题：{content}",
    input_variables=["content"]
)
# 旧写法：chain1 = LLMChain(llm=OpenAI(), prompt=prompt1)

# 步骤2：创建第二个Chain用于回答问题
prompt2 = PromptTemplate(
    template="基于以下上下文回答问题：\n上下文：{context}\n问题：{question}",
    input_variables=["context", "question"]
)
# 旧写法：chain2 = LLMChain(llm=OpenAI(), prompt=prompt2)

# 步骤3：手动组合多个Chain的输出（旧范式 LLMChain + chain.run 方式）
# 这里需要手动处理数据传递和格式转换
def combined_chain(input_data):
    # 第一步（旧写法：questions = chain1.run(content=input_data["content"])）
    questions = "问题1\n问题2\n问题3"
    # 第二步（假设我们取第一个问题）
    question = questions.split("\n")[0]
    # 第三步（旧写法：answer = chain2.run(context=input_data["context"], question=question)）
    answer = "基于上下文的回答"
    return answer

# 传统方式总共需要约30行代码，而且难以复用和测试
