from typing import Dict, Any, Optional
from task1_company_intelligence.graph import company_intelligence_graph
from common.logging_config import logger

# Session memory cache for multi-turn Task 1 queries
SESSION_STATE_CACHE: Dict[str, Dict[str, Any]] = {}

def run_company_intelligence_workflow(
    company_name: str,
    session_id: str = "default_session"
) -> Dict[str, Any]:
    """
    High-level entry point to execute the Task 1 LangGraph Company Intelligence workflow.
    Supports session-level context preservation for comparison or follow-up queries.
    """
    logger.info(f"Executing Company Intelligence Workflow for: '{company_name}' [Session: {session_id}]")
    
    # Check for comparative queries (e.g., "Compare it with AMD")
    prior_session = SESSION_STATE_CACHE.get(session_id)
    target_name = company_name
    
    if prior_session and ("compare" in company_name.lower() or "with" in company_name.lower()):
        prior_company = prior_session.get("company_name", "")
        if prior_company and prior_company.lower() not in company_name.lower():
            target_name = f"{company_name} (Previously analyzed: {prior_company})"

    initial_state = {
        "company_name": target_name,
        "collected_data": {},
        "news": [],
        "stock_data": {},
        "company_info": {},
        "analysis": {},
        "messages": [],
        "errors": [],
        "sources": [],
        "final_report": "",
        "session_id": session_id
    }

    config = {"configurable": {"thread_id": session_id}}

    try:
        final_state = company_intelligence_graph.invoke(initial_state, config=config)
        SESSION_STATE_CACHE[session_id] = final_state
        return final_state
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        return {
            "company_name": company_name,
            "final_report": f"### Error Running Intelligence Workflow\n\nUnable to complete analysis: {str(e)}",
            "errors": [str(e)],
            "sources": []
        }
