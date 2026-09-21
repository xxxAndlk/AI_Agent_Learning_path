from langchain.callbacks import StdOutCallbackHandler

chain.invoke(
    input,
    config={"callbacks": [StdOutCallbackHandler()]}
)
