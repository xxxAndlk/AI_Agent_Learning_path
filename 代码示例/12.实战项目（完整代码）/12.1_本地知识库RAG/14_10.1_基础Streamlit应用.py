# src/ui/streamlit_app.py
# Streamlit RAG应用
import streamlit as st
import os
from pathlib import Path
from typing import List, Optional
import time

# 设置页面配置
st.set_page_config(
    page_title="本地知识库问答系统",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 导入RAG组件
from src.pipeline.rag_pipeline import RAGPipeline
from config.config import Config

# 初始化配置
Config.init_dirs()

# 会话状态管理
if "rag_pipeline" not in st.session_state:
    st.session_state.rag_pipeline = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "messages" not in st.session_state:
    st.session_state.messages = []


def init_rag_pipeline() -> RAGPipeline:
    """初始化RAG管道
    
    从会话状态获取或创建RAG管道
    """
    if st.session_state.rag_pipeline is None:
        # 创建RAG管道
        rag = RAGPipeline(
            vector_store_type="faiss",
            llm_provider="openai",
            embedding_model="openai",
            chunk_size=500,
            chunk_overlap=100,
            top_k=3,
            verbose=False
        )
        
        # 尝试加载已有知识库
        if rag.load_vector_store():
            rag.setup_qa_chain()
            st.session_state.rag_pipeline = rag
            return rag
        else:
            return None
    
    return st.session_state.rag_pipeline


def build_knowledge_base(docs_dir: str) -> bool:
    """构建知识库
    
    参数:
        docs_dir: 文档目录
    返回:
        是否成功
    """
    try:
        rag = RAGPipeline(
            vector_store_type="faiss",
            llm_provider="openai",
            chunk_size=500,
            chunk_overlap=100,
            top_k=3
        )
        
        # 加载并处理文档
        chunks = rag.load_and_process_documents(docs_dir)
        
        # 设置问答链
        rag.setup_qa_chain()
        
        # 保存到会话状态
        st.session_state.rag_pipeline = rag
        
        return True
    except Exception as e:
        st.error(f"构建知识库失败: {e}")
        return False


def display_sources(sources: List[dict]):
    """显示参考来源
    
    参数:
        sources: 来源列表
    """
    with st.expander("📚 参考来源", expanded=False):
        for i, source in enumerate(sources):
            st.markdown(f"**来源 {i+1}**")
            st.markdown(f"```\n{source.get('content', '')}\n```")
            st.markdown(f"元数据: `{source.get('metadata', {})}`")
            st.divider()


def main():
    """主应用函数"""
    
    # 标题和介绍
    st.title("🤖 本地知识库问答系统")
    st.markdown("""
    这是一个基于RAG（检索增强生成）技术的本地知识库问答系统。
    您可以上传文档，系统会自动构建知识库，然后回答您的问题。
    """)
    
    # 侧边栏
    with st.sidebar:
        st.header("⚙️ 设置")
        
        st.subheader("知识库管理")
        
        # 文档目录输入
        docs_dir = st.text_input(
            "文档目录",
            value="./data/docs",
            help="存放文档的目录路径"
        )
        
        # 构建知识库按钮
        if st.button("🔨 构建知识库", type="primary"):
            with st.spinner("正在构建知识库..."):
                if build_knowledge_base(docs_dir):
                    st.success("✅ 知识库构建完成！")
        
        # 重新加载知识库按钮
        if st.button("📂 加载已有知识库"):
            rag = init_rag_pipeline()
            if rag:
                st.success("✅ 知识库加载成功！")
            else:
                st.warning("⚠️ 未找到已有知识库")
        
        st.divider()
        
        # 清空对话历史
        if st.button("🗑️ 清空对话历史"):
            st.session_state.chat_history = []
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        # 显示统计信息
        st.subheader("📊 统计信息")
        if st.session_state.rag_pipeline:
            st.info(f"知识库已加载")
            st.info(f"对话轮数: {len(st.session_state.chat_history)}")
    
    # 主聊天区域
    st.subheader("💬 对话")
    
    # 显示聊天消息
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 用户输入
    if prompt := st.chat_input("请输入您的问题..."):
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # 生成回答
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            message_placeholder.markdown("🤔 思考中...")
            
            try:
                rag = init_rag_pipeline()
                
                if rag is None:
                    message_placeholder.markdown(
                        "⚠️ 请先构建或加载知识库！"
                    )
                else:
                    # 执行查询
                    result = rag.query_with_conversation(
                        question=prompt,
                        chat_history=st.session_state.chat_history
                    )
                    
                    # 显示回答
                    answer = result["answer"]
                    message_placeholder.markdown(answer)
                    
                    # 显示来源
                    if "sources" in result and result["sources"]:
                        display_sources(result["sources"])
                    
                    # 保存到历史
                    st.session_state.chat_history.append((prompt, answer))
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer
                    })
                    
            except Exception as e:
                message_placeholder.markdown(f"❌ 错误: {e}")
    
    # 底部提示
    st.markdown("---")
    st.caption("💡 提示：您可以先在侧边栏设置文档目录并构建知识库")


if __name__ == "__main__":
    main()
