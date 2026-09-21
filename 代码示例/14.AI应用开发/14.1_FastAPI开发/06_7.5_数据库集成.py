# 使用SQLAlchemy进行数据库操作
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# 创建数据库引擎
DATABASE_URL = "sqlite:///./ai_app.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite专用
    poolclass=StaticPool,
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建基类
Base = declarative_base()


# 定义模型
class UserModel(Base):
    """用户数据库模型"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class ConversationModel(Base):
    """对话历史模型"""
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    user_id = Column(Integer, nullable=True)
    message = Column(String(2000), nullable=False)
    response = Column(String(5000))
    model_used = Column(String(50))
    tokens_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)


# 创建所有表
Base.metadata.create_all(bind=engine)


# 数据库依赖
def get_db() -> Generator[Session, None, None]:
    """获取数据库会话的依赖"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 集成到路由
from sqlalchemy.orm import Session


@api_router.post("/users/", response_model=UserResponse)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """创建用户（同步版本）"""
    # 检查用户是否已存在
    db_user = db.query(UserModel).filter(
        UserModel.username == user.username
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="用户名已存在")
    
    # 创建用户
    hashed_password = f"hashed_{user.password}"  # 实际应使用bcrypt
    db_user = UserModel(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@api_router.get("/users/", response_model=List[UserResponse])
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@api_router.post("/conversations/")
def save_conversation(
    session_id: str,
    message: str,
    response: str,
    model_used: str = "gpt-5.4-mini",
    tokens_used: int = 0,
    user_id: int = None,
    db: Session = Depends(get_db)
):
    """保存对话记录"""
    conversation = ConversationModel(
        session_id=session_id,
        user_id=user_id,
        message=message,
        response=response,
        model_used=model_used,
        tokens_used=tokens_used
    )
    db.add(conversation)
    db.commit()
    return {"id": conversation.id}


@api_router.get("/conversations/{session_id}")
def get_conversations(
    session_id: str,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """获取会话历史"""
    conversations = db.query(ConversationModel).filter(
        ConversationModel.session_id == session_id
    ).order_by(ConversationModel.created_at.desc()).limit(limit).all()
    
    return [
        {
            "id": c.id,
            "message": c.message,
            "response": c.response,
            "model_used": c.model_used,
            "created_at": c.created_at.isoformat()
        }
        for c in conversations
    ]


# 注册路由
app.include_router(api_router)
