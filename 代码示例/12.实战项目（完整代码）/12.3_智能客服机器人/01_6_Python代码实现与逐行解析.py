# 导入类型注解和依赖模块
from typing import Dict, List, Optional
from openai import OpenAI
from datetime import datetime
import json
import os

class SmartCustomerService:
    """智能客服系统
    
    功能：
    - 意图识别和分类：判断用户想要什么
    - 知识库问答：从企业知识库检索答案
    - 多轮对话管理：维护对话上下文
    - 情感分析：理解用户情绪
    - 会话历史记录：保存完整对话记录
    """
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # 知识库（简化版）：存储企业常见问题和政策
        self.knowledge_base = {
            "退款政策": """
            我们的退款政策如下：
            1. 7天内无理由退款
            2. 退款将在3-5个工作日原路返回
            3. 已使用服务不支持退款
            """,
            "发货时间": """
            发货时间说明：
            1. 标准订单：24小时内发货
            2. 定制订单：3-5个工作日发货
            3. 节假日可能延迟
            """,
            "会员权益": """
            会员权益包括：
            1. 全场商品9折优惠
            2. 每月2张免邮券
            3. 专属客服通道
            4. 新品优先体验
            """
        }
        
        # 会话存储：管理所有用户会话
        self.sessions: Dict[str, Dict] = {}
    
    def _classify_intent(self, user_input: str) -> str:
        """意图识别：分析用户输入，判断其意图类别
        
        参数:
            user_input: 用户输入的文本
        返回:
            意图类别字符串
        """
        intents = ["退款", "发货", "会员", "投诉", "咨询", "其他"]
        
        # 构建意图识别提示
        prompt = f"""请判断用户意图，从以下选项中选择最相关的一个：
意图选项：{', '.join(intents)}

用户输入：{user_input}

只回复意图名称，不要解释。"""
        
        # 调用LLM进行意图分类
        response = self.client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        
        intent = response.choices[0].message.content.strip()
        
        # 确保返回的意图在有效列表中
        for valid_intent in intents:
            if valid_intent in intent:
                return valid_intent
        
        return "其他"
    
    def _analyze_sentiment(self, user_input: str) -> Dict:
        """情感分析：分析文本的情感倾向和紧急程度
        
        参数:
            user_input: 用户输入的文本
        返回:
            包含情感倾向、置信度、紧急程度的字典
        """
        prompt = f"""分析以下文本的情感：

文本：{user_input}

请以JSON格式返回：
{{
    "sentiment": "positive/negative/neutral",
    "confidence": 0.0-1.0,
    "urgency": "high/medium/low"
}}"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}  # 要求JSON格式输出
            )
            
            return json.loads(response.choices[0].message.content)
        except:
            # 解析失败时返回默认值
            return {"sentiment": "neutral", "confidence": 0.5, "urgency": "low"}
    
    def _retrieve_knowledge(self, query: str, intent: str) -> str:
        """从知识库检索相关信息
        
        根据识别的意图从知识库中获取对应的政策或说明
        如果没有精确匹配，则返回全部知识内容
        """
        # 根据意图匹配知识
        if intent == "退款" and "退款政策" in self.knowledge_base:
            return self.knowledge_base["退款政策"]
        elif intent == "发货" and "发货时间" in self.knowledge_base:
            return self.knowledge_base["发货时间"]
        elif intent == "会员" and "会员权益" in self.knowledge_base:
            return self.knowledge_base["会员权益"]
        
        # 默认返回所有知识
        return "\n\n".join(self.knowledge_base.values())
    
    def _generate_response(self, user_input: str, context: Dict) -> str:
        """生成回复：结合上下文信息生成最终回答
        
        参数:
            user_input: 用户当前输入
            context: 包含意图、情感、历史等上下文字典
        返回:
            生成的回复文本
        """
        intent = context.get("intent", "咨询")
        sentiment = context.get("sentiment", {})
        history = context.get("history", [])
        
        # 检索知识
        knowledge = self._retrieve_knowledge(user_input, intent)
        
        # 构建提示词，包含情感和知识信息
        sentiment_info = f"用户情感: {sentiment.get('sentiment', 'neutral')}"
        urgency_info = f"紧急程度: {sentiment.get('urgency', 'low')}"
        
        prompt = f"""你是一个专业、友好的客服助手。

用户意图：{intent}
{sentiment_info}
{urgency_info}

相关知识：
{knowledge}

历史对话：
{self._format_history(history[-3:])}

用户当前输入：{user_input}

请提供专业、有帮助的回复。如果无法解决，请转接人工客服。"""
        
        response = self.client.chat.completions.create(
            model="gpt-5.4-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        return response.choices[0].message.content
    
    def _format_history(self, history: List[Dict]) -> str:
        """格式化历史对话：转换为可读的文本格式
        
        参数:
            history: 历史对话记录列表
        返回:
            格式化的历史对话文本
        """
        if not history:
            return "无"
        
        formatted = []
        for turn in history:
            formatted.append(f"用户: {turn.get('user', '')}")
            formatted.append(f"客服: {turn.get('agent', '')}")
        
        return "\n".join(formatted)
    
    def chat(self, user_input: str, session_id: str = "default") -> Dict:
        """对话入口：处理用户消息的主接口
        
        参数:
            user_input: 用户输入的文本
            session_id: 会话ID，用于区分不同用户
        返回:
            包含回复、意图、情感信息的字典
        """
        # 获取或创建会话
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "history": [],
                "created_at": datetime.now().isoformat()
            }
        
        session = self.sessions[session_id]
        
        # 1. 意图识别
        intent = self._classify_intent(user_input)
        
        # 2. 情感分析
        sentiment = self._analyze_sentiment(user_input)
        
        # 3. 生成上下文
        context = {
            "intent": intent,
            "sentiment": sentiment,
            "history": session["history"]
        }
        
        # 4. 生成回复
        response = self._generate_response(user_input, context)
        
        # 5. 保存对话历史
        session["history"].append({
            "user": user_input,
            "agent": response,
            "intent": intent,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        })
        
        return {
            "response": response,
            "intent": intent,
            "sentiment": sentiment,
            "session_id": session_id
        }
    
    def get_session_summary(self, session_id: str) -> Dict:
        """获取会话摘要：统计会话的各项指标
        
        参数:
            session_id: 会话ID
        返回:
            包含统计信息的字典
        """
        if session_id not in self.sessions:
            return {}
        
        session = self.sessions[session_id]
        history = session["history"]
        
        # 统计
        total_turns = len(history)
        intents = {}
        sentiments = {"positive": 0, "negative": 0, "neutral": 0}
        
        for turn in history:
            intent = turn.get("intent", "其他")
            intents[intent] = intents.get(intent, 0) + 1
            
            sentiment = turn.get("sentiment", {}).get("sentiment", "neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        return {
            "total_turns": total_turns,
            "intents": intents,
            "sentiments": sentiments,
            "created_at": session["created_at"]
        }

if __name__ == "__main__":
    # 创建客服系统实例
    service = SmartCustomerService()
    
    # 模拟对话
    print("=== 智能客服系统 ===\n")
    
    test_inputs = [
        "你好，我想了解一下退款政策",
        "那退款大概多久能到账呢？",
        "你们的发货速度太慢了，我很不满意！",
        "会员有什么特权吗？"
    ]
    
    session_id = "user_001"
    
    # 逐条处理用户输入
    for user_input in test_inputs:
        print(f"用户: {user_input}")
        result = service.chat(user_input, session_id)
        print(f"客服: {result['response']}")
        print(f"[意图: {result['intent']}, 情感: {result['sentiment']['sentiment']}]\n")
    
    # 打印会话摘要
    summary = service.get_session_summary(session_id)
    print("会话摘要:", json.dumps(summary, ensure_ascii=False, indent=2))
