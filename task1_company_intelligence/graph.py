from typing import Dict, Any
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from task1_company_intelligence.state import CompanyState
from task1_company_intelligence.agents.data_collector import DataCollectorAgent
from task1_company_intelligence.agents.analyst import AnalystAgent
from common.logging_config import logger

def controller_node(state: CompanyState) -> Dict[str, Any]:
    """
    Controller node that initializes workflow tracking, validates inputs,
    and sets up execution metadata.
    """
    company_name = state.get("company_name", "").strip()
    logger.info(f"--- CONTROLLER NODE: Initializing analysis workflow for '{company_name}' ---")
    
    messages = list(state.get("messages", []))
    messages.append(f"Controller initialized workflow for '{company_name}'.")
    
    return {
        "company_name": company_name,
        "messages": messages,
        "errors": state.get("errors", []),
        "sources": state.get("sources", [])
    }

def data_collector_node(state: CompanyState) -> Dict[str, Any]:
    """
    Node wrapper for DataCollectorAgent.
    """
    collector = DataCollectorAgent()
    return collector.run(state)

def analyst_node(state: CompanyState) -> Dict[str, Any]:
    """
    Node wrapper for AnalystAgent.
    """
    analyst = AnalystAgent()
    return analyst.run(state)

def create_company_intelligence_graph():
    """
    Constructs and compiles the real LangGraph StateGraph for Company Intelligence.
    """
    builder = StateGraph(CompanyState)

    builder.add_node("controller", controller_node)
    builder.add_node("data_collector", data_collector_node)
    builder.add_node("analyst", analyst_node)

    builder.add_edge(START, "controller")
    builder.add_edge("controller", "data_collector")
    builder.add_edge("data_collector", "analyst")
    builder.add_edge("analyst", END)

    memory = MemorySaver()
    compiled_graph = builder.compile(checkpointer=memory)
    return compiled_graph

company_intelligence_graph = create_company_intelligence_graph()
