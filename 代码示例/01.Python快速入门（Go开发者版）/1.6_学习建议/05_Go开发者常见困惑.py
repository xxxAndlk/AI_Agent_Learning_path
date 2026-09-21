# Python: asyncio + coroutine
async def main():
    task = asyncio.create_task(process_data())
    result = await task
