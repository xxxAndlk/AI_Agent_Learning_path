import asyncio
from asyncio import Queue

class AsyncWorkerPool:
    """asyncio Worker Pool（类似Go的Goroutine Pool）"""
    
    def __init__(self, max_workers=4):
        self.max_workers = max_workers
        self.task_queue = Queue()
        self.workers = []
    
    async def start(self):
        for i in range(self.max_workers):
            task = asyncio.create_task(self._worker(i))
            self.workers.append(task)
    
    async def _worker(self, worker_id):
        while True:
            try:
                coro, future = await self.task_queue.get()
                try:
                    result = await coro
                    future.set_result(result)
                except Exception as e:
                    future.set_exception(e)
                self.task_queue.task_done()
            except asyncio.CancelledError:
                break
    
    async def submit(self, coro):
        future = asyncio.get_running_loop().create_future()
        await self.task_queue.put((coro, future))
        return future
    
    async def shutdown(self):
        await self.task_queue.join()
        for worker in self.workers:
            worker.cancel()
        await asyncio.gather(*self.workers, return_exceptions=True)
