# src/ui/streamlit_app_enhanced.py
# 增强版Streamlit RAG应用
import streamlit as st
import os
from pathlib import Path
from typing import List, Dict, Any
import json

st.set_page_config(
    page_title="RAG智能问答助手",
    page_icon="🧠",
    layout="wide"
)

# 样式定制
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    .source-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .metric-card {
        background-color: #e8f4f8;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitRAGApp:
    """Streamlit RAG应用类
    
    封装RAG应用的所有功能
    """
    
    def __init__(self):
        self._init_session_state()
    
    def _init_session_state(self):
        """初始化会话状态"""
        defaults = {
            "rag_pipeline": None,
            "chat_history": [],
            "messages": [],
            "retrieval_results": [],
            "show_sources": True,
            "temperature": 0.0,
            "top_k": 3
        }
        
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value
    
    def render_header(self):
        """渲染头部"""
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown(
                '<p class="main-header">🧠 RAG智能问答助手</p>',
                unsafe_allow_html=True
            )
    
    def render_sidebar(self):
        """渲染侧边栏"""
        with st.sidebar:
            st.title("⚙️ 配置")
            
            # 知识库管理
            st.header("📚 知识库")
            
            # 文档目录
            docs_dir = st.text_input(
                "文档目录",
                value="./data/docs",
                key="docs_dir"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("构建", type="primary", use_container_width=True):
                    self._build_knowledge_base(docs_dir)
            with col2:
                if st.button("加载", use_container_width=True):
                    self._load_knowledge_base()
            
            st.divider()
            
            # 检索设置
            st.header("🔍 检索设置")
            
            # Top K
            top_k = st.slider(
                "返回结果数量",
                min_value=1,
                max_value=10,
                value=st.session_state.top_k,
                key="top_k_slider"
            )
            st.session_state.top_k = top_k
            
            # 显示来源
            show_sources = st.checkbox(
                "显示参考来源",
                value=st.session_state.show_sources,
                key="show_sources_checkbox"
            )
            st.session_state.show_sources = show_sources
            
            st.divider()
            
            # 统计信息
            st.header("📊 统计")
            self._render_stats()
            
            st.divider()
            
            # 工具
            st.header("🔧 工具")
            
            if st.button("清空对话", use_container_width=True):
                self._clear_chat()
            
            if st.button("导出对话", use_container_width=True):
                self._export_chat()
            
            # 文件上传
            st.header("📤 上传文档")
            uploaded_files = st.file_uploader(
                "选择文件",
                type=["txt", "pdf", "docx", "md"],
                accept_multiple_files=True
            )
            
            if uploaded_files:
                self._handle_file_upload(uploaded_files, docs_dir)
    
    def _render_stats(self):
        """渲染统计信息"""
        if st.session_state.rag_pipeline:
            st.metric("知识库状态", "已加载")
        else:
            st.metric("知识库状态", "未加载")
        
        st.metric("对话轮数", len(st.session_state.chat_history))
        st.metric("消息数量", len(st.session_state.messages))
    
    def _build_knowledge_base(self, docs_dir: str):
        """构建知识库"""
        from src.pipeline.rag_pipeline import RAGPipeline
        
        with st.spinner("正在构建知识库..."):
            try:
                rag = RAGPipeline(
                    vector_store_type="faiss",
                    chunk_size=500,
                    chunk_overlap=100,
                    top_k=st.session_state.top_k
                )
                
                chunks = rag.load_and_process_documents(docs_dir)
                rag.setup_qa_chain()
                
                st.session_state.rag_pipeline = rag
                
                st.success(f"✅ 知识库构建完成！共处理 {len(chunks)} 个文档块")
                
            except Exception as e:
                st.error(f"构建失败: {e}")
    
    def _load_knowledge_base(self):
        """加载知识库"""
        from src.pipeline.rag_pipeline import RAGPipeline
        
        try:
            rag = RAGPipeline(
                vector_store_type="faiss",
                top_k=st.session_state.top_k
            )
            
            if rag.load_vector_store():
                rag.setup_qa_chain()
                st.session_state.rag_pipeline = rag
                st.success("✅ 知识库加载成功！")
            else:
                st.warning("⚠️ 未找到已构建的知识库")
                
        except Exception as e:
            st.error(f"加载失败: {e}")
    
    def _handle_file_upload(self, files, target_dir: str):
        """处理文件上传"""
        import shutil
        
        target_path = Path(target_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        saved_count = 0
        
        for file in files:
            dest = target_path / file.name
            with open(dest, "wb") as f:
                f.write(file.getbuffer())
            saved_count += 1
        
        st.success(f"已保存 {saved_count} 个文件到 {target_dir}")
    
    def _clear_chat(self):
        """清空对话"""
        st.session_state.chat_history = []
        st.session_state.messages = []
        st.rerun()
    
    def _export_chat(self):
        """导出对话"""
        export_data = {
            "chat_history": st.session_state.chat_history,
            "messages": st.session_state.messages
        }
        
        st.download_button(
            label="下载对话记录",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name="chat_history.json",
            mime="application/json"
        )
    
    def render_chat(self):
        """渲染聊天区域"""
        st.subheader("💬 对话")
        
        # 聊天容器
        chat_container = st.container()
        
        with chat_container:
            for i, msg in enumerate(st.session_state.messages):
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    
                    # 如果是助手消息，显示来源
                    if msg["role"] == "assistant" and st.session_state.show_sources:
                        if i < len(st.session_state.retrieval_results):
                            results = st.session_state.retrieval_results[i]
                            self._render_sources(results)
        
        # 用户输入
        if prompt := st.chat_input("请输入您的问题..."):
            self._handle_user_input(prompt)
    
    def _handle_user_input(self, prompt: str):
        """处理用户输入"""
        # 添加用户消息
        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })
        
        # 生成回答
        if st.session_state.rag_pipeline is None:
            st.error("请先构建或加载知识库！")
            return
        
        with st.spinner("思考中..."):
            try:
                # 查询
                result = st.session_state.rag_pipeline.query_with_conversation(
                    question=prompt,
                    chat_history=st.session_state.chat_history
                )
                
                # 添加助手消息
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": result["answer"]
                })
                
                # 保存检索结果
                st.session_state.retrieval_results.append(result.get("sources", []))
                
                # 更新历史
                st.session_state.chat_history.append((prompt, result["answer"]))
                
                st.rerun()
                
            except Exception as e:
                st.error(f"查询失败: {e}")
    
    def _render_sources(self, sources: List[Dict]):
        """渲染来源"""
        if not sources:
            return
        
        with st.expander("📚 参考来源", expanded=False):
            for i, source in enumerate(sources):
                st.markdown(f"**来源 {i+1}**")
                st.caption(source.get("content", ""))
                st.markdown(f"_{source.get('metadata', {})}_")
    
    def render(self):
        """渲染整个应用"""
        self.render_header()
        self.render_sidebar()
        self.render_chat()


def main():
    """主函数"""
    app = StreamlitRAGApp()
    app.render()


if __name__ == "__main__":
    main()
