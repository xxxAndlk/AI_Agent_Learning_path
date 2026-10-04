# LCEL方式：使用管道操作符
chain = prompt | llm | StrOutputParser()
result = chain.invoke({"topic": "人工智能"})
