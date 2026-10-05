# pyrefly: ignore [missing-import]
import streamlit as st
import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common.config import settings
from task2_knowledge_bot.memory import memory_manager
from frontend.task1_ui import render_task1_ui
from frontend.task2_ui import render_task2_ui

def main():
    st.set_page_config(
        page_title="Soulpage GenAI Technical Assignment",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Sidebar configuration
    st.sidebar.title("⚙️ Control Panel")
    
    # Model Provider status
    st.sidebar.markdown(f"**LLM Provider:** `{settings.MODEL_PROVIDER.upper()}`")
    st.sidebar.markdown(f"**Model Name:** `{settings.MODEL_NAME}`")
    
    # Demo Mode Status Indicator
    if settings.DEMO_MODE:
        st.sidebar.warning("⚠️ **DEMO MODE ACTIVE**\n(Using structured fallback data without paid API keys)")
    else:
        st.sidebar.success("🟢 **LIVE API MODE ACTIVE**")

    st.sidebar.markdown("---")

    # Session ID Management
    session_id = st.sidebar.text_input("Session ID:", value="demo-session", key="app_session_id")

    if st.sidebar.button("🧹 Clear Chat History", type="secondary", use_container_width=True):
        memory_manager.clear_history(session_id)
        if "task1_result" in st.session_state:
            del st.session_state["task1_result"]
        st.sidebar.success(f"Cleared session '{session_id}'!")
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("📌 About")
    st.sidebar.info(
        "**Soulpage GenAI Technical Assignment**\n\n"
        "- **Task 1:** LangGraph Multi-Agent Company Intelligence\n"
        "- **Task 2:** Conversational Knowledge Bot with memory & tool calling\n\n"
        "Built with LangGraph, LangChain, FastAPI & Streamlit."
    )

    # Header Title
    st.title("🧠 Soulpage GenAI Architecture Demo")
    st.write("Production-quality GenAI systems built with LangGraph, LangChain, FastAPI, and Streamlit.")

    # Main Tabs
    tab1, tab2 = st.tabs([
        "🏢 Task 1: Multi-Agent Company Intelligence",
        "💬 Task 2: Conversational Knowledge Bot"
    ])

    with tab1:
        render_task1_ui(session_id)

    with tab2:
        render_task2_ui(session_id)

if __name__ == "__main__":
    main()
