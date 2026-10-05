# pyrefly: ignore [missing-import]
import streamlit as st
from task1_company_intelligence.workflow import run_company_intelligence_workflow

def render_task1_ui(session_id: str):
    st.header("🏢 Task 1: Multi-Agent Company Intelligence")
    st.caption("Powered by LangGraph StateGraph, Data Collector Agent, and Analyst Agent")

    col1, col2 = st.columns([3, 1])
    with col1:
        company_input = st.text_input(
            "Enter Company Name or Ticker:",
            placeholder="e.g. NVIDIA, Microsoft, Apple",
            key="task1_company_input"
        )
    with col2:
        st.write(" ")
        st.write(" ")
        analyze_btn = st.button("🚀 Analyze Company", type="primary", use_container_width=True)

    if analyze_btn:
        if not company_input.strip():
            st.warning("Please enter a valid company name.")
            return

        with st.spinner(f"Orchestrating Multi-Agent Workflow for '{company_input}'..."):
            # Render Workflow Pipeline Visualizer
            status_container = st.status("⚡ LangGraph Workflow Execution Pipeline", expanded=True)
            status_container.write("1️⃣ **Controller Node**: Initializing graph state and sequence metadata...")
            status_container.write("2️⃣ **Data Collector Agent**: Executing News, Stock, and Company tools...")
            
            result = run_company_intelligence_workflow(
                company_name=company_input.strip(),
                session_id=session_id
            )

            status_container.write("3️⃣ **Analyst Agent**: Synthesizing facts, risks, and strategic opportunities...")
            status_container.write("4️⃣ **Report Generator**: Formatting executive summary markdown...")
            status_container.update(label="✅ LangGraph Workflow Completed Successfully!", state="complete", expanded=False)

        # Store in session state for tab persistence
        st.session_state["task1_result"] = result

    # Display results if available in session state
    if "task1_result" in st.session_state:
        res = st.session_state["task1_result"]
        collected = res.get("collected_data", {})
        stock = res.get("stock_data", {})
        info = res.get("company_info", {})
        report = res.get("final_report", "")

        # Top Metric Cards
        st.subheader(f"Results: {res.get('company_name', 'Target Company')}")
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        with m_col1:
            st.metric("Ticker Symbol", stock.get("symbol", "N/A"))
        with m_col2:
            st.metric("Market Price", f"${stock.get('price', 'N/A')}")
        with m_col3:
            pct = stock.get("change_percent", 0.0)
            st.metric("Price Change", f"{pct}%", delta=pct if isinstance(pct, (int, float)) else None)
        with m_col4:
            if stock.get("demo_data", False):
                st.info("⚠️ DEMO MODE DATA")
            else:
                st.success("🟢 LIVE DATA")

        # Company Info Card
        if info:
            with st.expander("ℹ️ Company Profile Metadata", expanded=False):
                st.write(f"**Description:** {info.get('description', 'N/A')}")
                st.write(f"**Industry:** {info.get('industry', 'N/A')}")
                st.write(f"**Headquarters:** {info.get('headquarters', 'N/A')}")
                st.write(f"**Website:** [{info.get('website', '#')}]({info.get('website', '#')})")

        # Full Report Render
        st.markdown("---")
        st.markdown(report)
