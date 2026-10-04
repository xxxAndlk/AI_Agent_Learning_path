import json
from langchain.memory import ConversationBufferMemory
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

class MySQLMemory(ConversationBufferMemory):
    """MySQL持久化Memory"""
    
    def __init__(self, user_id: str, db_config: dict, **kwargs):
        import pymysql
        super().__init__(**kwargs)
        self.user_id = user_id
        self.db_config = db_config
        self._connection = None
        self._init_db()
        self._load_from_db()
    
    def _get_connection(self):
        import pymysql
        if self._connection is None or not self._connection.open:
            self._connection = pymysql.connect(**self.db_config)
        return self._connection
    
    def _init_db(self):
        """初始化数据库表"""
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversation_memory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255) NOT NULL,
                    message_type VARCHAR(50),
                    content TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_user_id (user_id)
                )
            """)
            conn.commit()
    
    def _load_from_db(self):
        """从数据库加载"""
        conn = self._get_connection()
        with conn.cursor(pymysql.cursors.DictCursor) as cursor:
            cursor.execute(
                "SELECT message_type, content FROM conversation_memory WHERE user_id = %s ORDER BY created_at",
                (self.user_id,)
            )
            for row in cursor.fetchall():
                if row["message_type"] == "human":
                    self.chat_memory.add_message(HumanMessage(content=row["content"]))
                elif row["message_type"] == "ai":
                    self.chat_memory.add_message(AIMessage(content=row["content"]))
    
    def _save_to_db(self, message_type: str, content: str):
        """保存到数据库"""
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO conversation_memory (user_id, message_type, content) VALUES (%s, %s, %s)",
                (self.user_id, message_type, content)
            )
            conn.commit()
    
    def save_context(self, inputs: dict, output: str) -> None:
        super().save_context(inputs, output)
        # 手动保存最后的消息到数据库
        messages = self.chat_memory.messages
        if messages:
            last_msg = messages[-1]
            msg_type = "human" if isinstance(last_msg, HumanMessage) else "ai"
            self._save_to_db(msg_type, last_msg.content)
    
    def clear(self) -> None:
        super().clear()
        conn = self._get_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM conversation_memory WHERE user_id = %s", (self.user_id,))
            conn.commit()


# Redis持久化示例
class RedisMemory(ConversationBufferMemory):
    """Redis持久化Memory"""
    
    def __init__(self, user_id: str, redis_config: dict, **kwargs):
        import redis
        super().__init__(**kwargs)
        self.user_id = user_id
        self.redis_client = redis.Redis(**redis_config)
        self.key = f"memory:{user_id}"
        self._load_from_redis()
    
    def _load_from_redis(self):
        """从Redis加载"""
        import json
        data = self.redis_client.get(self.key)
        if data:
            messages_data = json.loads(data)
            for msg in messages_data:
                if msg["type"] == "human":
                    self.chat_memory.add_message(HumanMessage(content=msg["content"]))
                elif msg["type"] == "ai":
                    self.chat_memory.add_message(AIMessage(content=msg["content"]))
    
    def _save_to_redis(self):
        """保存到Redis"""
        import json
        messages = []
        for msg in self.chat_memory.messages:
            msg_type = "human" if isinstance(msg, HumanMessage) else "ai"
            messages.append({"type": msg_type, "content": msg.content})
        self.redis_client.set(self.key, json.dumps(messages))
    
    def save_context(self, inputs: dict, output: str) -> None:
        super().save_context(inputs, output)
        self._save_to_redis()
    
    def clear(self) -> None:
        super().clear()
        self.redis_client.delete(self.key)
