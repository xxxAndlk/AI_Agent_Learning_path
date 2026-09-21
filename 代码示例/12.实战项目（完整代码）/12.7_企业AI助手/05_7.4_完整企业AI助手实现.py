class EnterpriseKnowledgeBase:
    """企业知识库 - 完整版"""
    
    def __init__(self):
        self.documents: Dict[str, Dict] = {}
        self._init_default_knowledge()
    
    def _init_default_knowledge(self):
        """初始化默认知识"""
        self.documents = {
            "休假政策": {
                "content": """公司员工休假政策：
1. 年假：入职满1年享受5天年假，满3年享受10天，满5年享受15天
2. 病假：需提供医院证明，每年最多15天
3. 事假：需提前申请，每年最多5天
4. 婚假：法定婚假3天，公司额外给予2天
5. 产假：法定产假98天，公司额外给予30天
6. 年假按自然年计算，可累积至多15天""",
                "category": "HR",
                "keywords": ["年假", "休假", "请假", "病假", "事假", "婚假", "产假"]
            },
            "报销流程": {
                "content": """费用报销流程：
1. 费用发生后30天内提交报销申请
2. 准备报销材料：发票、付款凭证、费用说明
3. 填写报销单，部门主管审批
4. 财务部门审核
5. 出纳付款（每周二、五付款）
注意事项：
- 发票必须为合规发票
- 差旅费用需附行程说明
- 餐饮费用每人每餐不超过150元""",
                "category": "财务",
                "keywords": ["报销", "发票", "费用", "付款", "差旅"]
            },
            "IT支持": {
                "content": """IT技术支持服务：
1. 服务热线：4000-1234（工作日9:00-18:00）
2. 邮箱支持：it@company.com
3. 常见问题：
   - 电脑故障：联系IT报修
   - 账号问题：重置密码需要身份验证
   - 软件安装：提交申请单
   - 网络问题：检查网络连接，必要时联系IT
4. 新设备申请：提交设备申请单，部门主管审批""",
                "category": "IT",
                "keywords": ["IT", "电脑", "网络", "账号", "密码", "软件"]
            },
            "会议室预约": {
                "content": """会议室预约规则：
1. 预约方式：内部系统预约或联系行政部
2. 会议室列表：
   - A101（10人）适合小型会议
   - A201（20人）适合中型会议
   - 大会堂（100人）适合大型会议
3. 预约规则：
   - 提前预约，最长可预约30天
   - 取消需提前2小时
   - 逾期未使用将记录违规
4. 注意事项：
   - 会议期间请保持安静
   - 使用完毕后请恢复原状""",
                "category": "行政",
                "keywords": ["会议", "会议室", "预约", "预定"]
            },
            "邮件发送": {
                "content": """企业邮箱使用规范：
1. 发送邮件：
   - 内部邮件：同事姓名@company.com
   - 外部邮件：username@company.com
2. 附件限制：单个附件最大25MB
3. 重要邮件需使用已读回执
4. 禁止发送：商业广告、敏感信息、非法内容
5. 邮件签名：必须包含姓名、部门、联系方式""",
                "category": "IT",
                "keywords": ["邮件", "邮箱", "发送", "附件"]
            },
            "员工福利": {
                "content": """员工福利政策：
1. 五险一金：入职即缴纳
2. 商业保险：意外伤害险、医疗保险
3. 年度体检：每年4月统一安排
4. 节日礼品：春节、中秋、生日
5. 员工活动：年度旅游、运动会、团建
6. 培训发展：内部培训、外部培训、学历补贴
7. 绩效奖金：每年1月、7月发放""",
                "category": "HR",
                "keywords": ["福利", "保险", "体检", "奖金", "培训", "活动"]
            }
        }
    
    def search(self, query: str, category: Optional[str] = None) -> List[Dict]:
        """搜索知识"""
        results = []
        query_lower = query.lower()
        
        for title, data in self.documents.items():
            # 分类过滤
            if category and data["category"] != category:
                continue
            
            # 关键词匹配
            for keyword in data["keywords"]:
                if keyword in query_lower:
                    results.append({
                        "title": title,
                        "content": data["content"],
                        "category": data["category"],
                        "relevance": 1.0
                    })
                    break
        
        return results


class EnterpriseAIAssistant:
    """企业AI助手 - 完整版"""
    
    def __init__(self):
        # 初始化各组件
        self.knowledge_base = EnterpriseKnowledgeBase()
        self.permission_manager = PermissionManager()
        self.audit_logger = AuditLogger()
        
        # 会话管理
        self.sessions: Dict[str, Dict] = {}
        
        # 意图识别模式
        self.intent_patterns = {
            IntentType.KNOWLEDGE_QUERY: ["政策", "流程", "规定", "制度", "是什么", "怎么", "如何"],
            IntentType.BOOK_MEETING: ["预约", "预定", "会议室", "会议"],
            IntentType.SEND_EMAIL: ["邮件", "发送", "发邮件", "写信"],
            IntentType.IT_SUPPORT: ["IT", "电脑", "网络", "密码", "账号", "软件"],
            IntentType.HR_POLICY: ["休假", "请假", "年假", "病假", "福利", "报销"],
        }
        
        logger.info("企业AI助手初始化完成")
    
    def _identify_intent(self, query: str) -> IntentType:
        """识别用户意图"""
        query_lower = query.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if pattern in query_lower:
                    return intent
        
        return IntentType.GENERAL
    
    def _execute_tool(
        self,
        intent: IntentType,
        params: Dict,
        user_id: str
    ) -> Dict:
        """执行工具调用"""
        result = {"success": False, "message": ""}
        
        # 检查权限
        tool_permission_map = {
            IntentType.BOOK_MEETING: "tool:meeting:book",
            IntentType.SEND_EMAIL: "tool:email:send",
            IntentType.KNOWLEDGE_QUERY: "knowledge:read"
        }
        
        required_permission = tool_permission_map.get(intent)
        if required_permission:
            if not self.permission_manager.check_permission(user_id, required_permission):
                result["message"] = "您没有执行此操作的权限"
                return result
        
        # 执行对应的工具
        if intent == IntentType.BOOK_MEETING:
            result = self._book_meeting(params)
        elif intent == IntentType.SEND_EMAIL:
            result = self._send_email(params)
        elif intent == IntentType.CREATE_TASK:
            result = self._create_task(params)
        
        # 记录工具调用
        self.audit_logger.log(
            user_id=user_id,
            action=f"tool_call:{intent.value}",
            resource="tools",
            details={"intent": intent.value, "params": params, "result": result}
        )
        
        return result
    
    def _book_meeting(self, params: Dict) -> Dict:
        """预约会议室"""
        room = params.get("room", "A101")
        time = params.get("time", "待确认")
        
        meeting_id = f"MT{ datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        return {
            "success": True,
            "message": f"已为您预约会议室{room}，时间：{time}",
            "meeting_id": meeting_id,
            "details": {"room": room, "time": time}
        }
    
    def _send_email(self, params: Dict) -> Dict:
        """发送邮件"""
        to = params.get("to", "")
        subject = params.get("subject", "")
        
        return {
            "success": True,
            "message": f"邮件已发送给 {to}",
            "email_id": f"EM{ datetime.now().strftime('%Y%m%d%H%M%S')}",
            "details": {"to": to, "subject": subject}
        }
    
    def _create_task(self, params: Dict) -> Dict:
        """创建任务"""
        task_name = params.get("task_name", "")
        
        return {
            "success": True,
            "message": f"任务 '{task_name}' 已创建",
            "task_id": f"TSK{ datetime.now().strftime('%Y%m%d%H%M%S')}",
            "details": {"task_name": task_name}
        }
    
    def chat(
        self,
        user_input: str,
        user_id: str = "guest",
        session_id: Optional[str] = None
    ) -> Dict:
        """主对话接口"""
        
        # 生成会话ID
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 创建消息记录
        message_id = str(uuid.uuid4())
        
        # 记录用户消息
        self.audit_logger.log(
            user_id=user_id,
            action="user_message",
            resource="chat",
            details={"session_id": session_id, "message": user_input}
        )
        
        # 意图识别
        intent = self._identify_intent(user_input)
        
        # 处理不同的意图
        response = ""
        knowledge_used = False
        
        if intent in [IntentType.KNOWLEDGE_QUERY, IntentType.HR_POLICY]:
            # 知识查询
            search_results = self.knowledge_base.search(user_input)
            if search_results:
                knowledge_used = True
                result = search_results[0]
                response = f"根据{result['category']}：\n\n{result['content']}"
            else:
                response = "抱歉，我没有找到相关信息。建议您联系IT支持或HR部门获取帮助。"
        
        elif intent == IntentType.BOOK_MEETING:
            # 预约会议
            tool_result = self._execute_tool(IntentType.BOOK_MEETING, {}, user_id)
            response = tool_result.get("message", "会议预约失败")
        
        elif intent == IntentType.SEND_EMAIL:
            # 发送邮件
            tool_result = self._execute_tool(IntentType.SEND_EMAIL, {
                "to": "收件人",
                "subject": "邮件主题"
            }, user_id)
            response = tool_result.get("message", "邮件发送失败")
        
        else:
            # 一般对话
            response = """您好！我是企业AI助手，可以为您提供以下服务：

1. 查询公司政策（年假、报销、福利等）
2. 预约会议室
3. 发送邮件
4. IT支持咨询
5. 创建任务

请告诉我您需要什么帮助？"""
        
        # 构建返回结果
        result = {
            "message_id": message_id,
            "session_id": session_id,
            "response": response,
            "intent": intent.value,
            "knowledge_used": knowledge_used,
            "timestamp": datetime.now().isoformat()
        }
        
        # 记录助手回复
        self.audit_logger.log(
            user_id=user_id,
            action="assistant_message",
            resource="chat",
            details={
                "session_id": session_id,
                "message": response,
                "intent": intent.value
            }
        )
        
        return result
    
    def get_session_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[Dict]:
        """获取会话历史"""
        # 简化实现
        return []
    
    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.sessions:
            del self.sessions[session_id]


# 运行完整企业AI助手
def demo_enterprise_assistant():
    """演示企业AI助手"""
    
    assistant = EnterpriseAIAssistant()
    
    # 测试查询
    test_cases = [
        ("请问年假政策是什么？", "emp001"),
        ("帮我预约明天上午10点的会议室", "emp001"),
        ("报销需要什么材料？", "hr001"),
        ("发送邮件给张三", "emp001")
    ]
    
    print("=" * 50)
    print("企业AI助手演示")
    print("=" * 50)
    
    for query, user_id in test_cases:
        print(f"\n用户({user_id}): {query}")
        result = assistant.chat(query, user_id)
        print(f"助手: {result['response'][:100]}...")
        print(f"意图识别: {result['intent']}")
    
    # 查询审计日志
    print("\n" + "=" * 50)
    print("审计日志")
    print("=" * 50)
    logs = assistant.audit_logger.get_logs(limit=5)
    for log in logs:
        print(f"[{log['timestamp']}] {log['user_id']}: {log['action']}")


if __name__ == "__main__":
    demo_enterprise_assistant()
