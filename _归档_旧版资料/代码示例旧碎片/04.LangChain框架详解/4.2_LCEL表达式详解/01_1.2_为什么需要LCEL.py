# 传统方式（v0.x 旧范式：LLMChain 在 v1.x 中已迁移至 langchain-classic，仅作迁移对照）
# from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

# 创建Prompt模板
prompt = PromptTemplate(
    template="请用一句话解释{topic}",
    input_variables=["topic"]
)

# v1.x 推荐使用聊天模型
llm = ChatOpenAI(model="gpt-5.4-mini", temperature=0.7)

# 旧写法：chain = LLMChain(llm=llm, prompt=prompt)
# 旧写法：result = chain.run(topic="人工智能")
# v1.x 推荐改用下方 LCEL 组合方式
