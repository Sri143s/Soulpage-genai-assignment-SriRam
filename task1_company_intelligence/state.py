from typing import TypedDict, List, Dict, Any, Optional

class CompanyState(TypedDict, total=False):
    """
    Strongly typed state for Task 1 Company Intelligence multi-agent workflow.
    Moves data sequentially through LangGraph nodes.
    """
    company_name: str
    collected_data: Dict[str, Any]
    news: List[Dict[str, Any]]
    stock_data: Dict[str, Any]
    company_info: Dict[str, Any]
    analysis: Dict[str, Any]
    messages: List[Any]
    errors: List[str]
    sources: List[Dict[str, Any]]
    final_report: str
    session_id: Optional[str]
