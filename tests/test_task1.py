import pytest
from task1_company_intelligence.state import CompanyState
from task1_company_intelligence.agents.data_collector import DataCollectorAgent
from task1_company_intelligence.agents.analyst import AnalystAgent
from task1_company_intelligence.workflow import run_company_intelligence_workflow

def test_company_state():
    state: CompanyState = {
        "company_name": "NVIDIA",
        "collected_data": {},
        "news": [],
        "stock_data": {},
        "company_info": {},
        "analysis": {},
        "messages": [],
        "errors": [],
        "sources": [],
        "final_report": ""
    }
    assert state["company_name"] == "NVIDIA"

def test_data_collector_agent():
    agent = DataCollectorAgent()
    initial_state: CompanyState = {
        "company_name": "Microsoft",
        "errors": [],
        "sources": []
    }
    out = agent.run(initial_state)
    assert "collected_data" in out
    assert "news" in out
    assert "stock_data" in out
    assert "company_info" in out
    assert out["company_info"]["company_name"] != ""

def test_analyst_agent():
    collector = DataCollectorAgent()
    state = collector.run({"company_name": "Apple", "errors": [], "sources": []})
    state["company_name"] = "Apple"

    analyst = AnalystAgent()
    analysis_out = analyst.run(state)
    assert "analysis" in analysis_out
    assert "final_report" in analysis_out
    assert "# 📊 Corporate Intelligence Report: Apple" in analysis_out["final_report"]

def test_company_intelligence_workflow_end_to_end():
    result = run_company_intelligence_workflow("NVIDIA", session_id="test-session-1")
    assert result is not None
    assert "final_report" in result
    assert len(result.get("final_report", "")) > 100
    assert "sources" in result
