class Runnable(ABC):
    def invoke(self, input) -> Output:
        """同步调用"""
        pass
    
    async def ainvoke(self, input) -> Output:
        """异步调用"""
        pass
    
    def stream(self, input) -> Iterator[Output]:
        """流式输出"""
        pass
    
    async def astream(self, input) -> AsyncIterator[Output]:
        """异步流式"""
        pass
    
    def batch(self, inputs) -> List[Output]:
        """批处理"""
        pass
