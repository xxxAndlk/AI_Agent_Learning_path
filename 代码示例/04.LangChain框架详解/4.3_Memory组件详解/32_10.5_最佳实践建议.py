import threading
import queue
import json

class AsyncPersistentMemory(ConversationBufferMemory):
    """异步持久化Memory"""
    
    def __init__(self, file_path: str, **kwargs):
        super().__init__(**kwargs)
        self.file_path = file_path
        self.write_queue = queue.Queue()
        self.write_thread = threading.Thread(target=self._write_worker, daemon=True)
        self.write_thread.start()
        self._load_from_file()
    
    def _write_worker(self):
        """后台写入线程"""
        while True:
            message = self.write_queue.get()
            if message is None:
                break
            self._append_to_file(message)
    
    def _append_to_file(self, message: dict):
        """追加写入文件"""
        import os
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        else:
            data = {"messages": []}
        
        data["messages"].append(message)
        
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def save_context(self, inputs: dict, output: str) -> None:
        super().save_context(inputs, output)
        # 异步写入
        messages = self.chat_memory.messages
        if messages:
            last_msg = messages[-1]
            msg_type = "human" if isinstance(last_msg, HumanMessage) else "ai"
            self.write_queue.put({"type": msg_type, "content": last_msg.content})
    
    def close(self):
        """关闭写入线程"""
        self.write_queue.put(None)
        self.write_thread.join()
