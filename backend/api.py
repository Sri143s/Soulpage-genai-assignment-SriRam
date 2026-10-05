from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from common.config import settings
from common.logging_config import logger
from task1_company_intelligence.workflow import run_company_intelligence_workflow
from task2_knowledge_bot.bot import knowledge_bot
from task2_knowledge_bot.memory import memory_manager

router = APIRouter(prefix="/api")

# Request / Response Pydantic Models
class HealthResponse(BaseModel):
    status: str = "healthy"
    demo_mode: bool
    model_provider: str
    model_name: str

class CompanyAnalyzeRequest(BaseModel):
    company: str = Field(..., description="Name of the target company to analyze")
    session_id: Optional[str] = Field("default_session", description="Session identifier")

class CompanyAnalyzeResponse(BaseModel):
    company: str
    report: str
    structured_data: Dict[str, Any]
    sources: List[Dict[str, Any]]
    errors: List[str]

class ChatRequest(BaseModel):
    session_id: str = Field("demo-session", description="Session identifier for chat memory")
    message: str = Field(..., description="User question or prompt")

class ChatResponse(BaseModel):
    session_id: str
    response: str
    resolved_query: Optional[str] = None
    sources: List[Dict[str, Any]]

class ClearChatRequest(BaseModel):
    session_id: str = Field(..., description="Session ID to clear history")

class ClearChatResponse(BaseModel):
    session_id: str
    status: str

@router.get("/health", response_model=HealthResponse, tags=["System"])
async def health_check():
    """
    Returns API health status and runtime LLM settings.
    """
    return HealthResponse(
        status="healthy",
        demo_mode=settings.DEMO_MODE,
        model_provider=settings.MODEL_PROVIDER,
        model_name=settings.MODEL_NAME
    )

@router.post("/company/analyze", response_model=CompanyAnalyzeResponse, tags=["Task 1"])
async def analyze_company(req: CompanyAnalyzeRequest):
    """
    Task 1: Triggers the LangGraph Multi-Agent Company Intelligence workflow.
    """
    logger.info(f"API Request: /api/company/analyze for '{req.company}'")
    if not req.company or not req.company.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company name must not be empty."
        )

    try:
        result = run_company_intelligence_workflow(
            company_name=req.company.strip(),
            session_id=req.session_id or "default_session"
        )
        return CompanyAnalyzeResponse(
            company=result.get("company_name", req.company),
            report=result.get("final_report", "No report generated."),
            structured_data=result.get("collected_data", {}),
            sources=result.get("sources", []),
            errors=result.get("errors", [])
        )
    except Exception as e:
        logger.error(f"API Error in /api/company/analyze: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing company intelligence workflow: {str(e)}"
        )

@router.post("/chat", response_model=ChatResponse, tags=["Task 2"])
async def chat_with_bot(req: ChatRequest):
    """
    Task 2: Conversational Knowledge Bot query endpoint.
    """
    logger.info(f"API Request: /api/chat [Session: {req.session_id}]")
    if not req.message or not req.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message content must not be empty."
        )

    try:
        bot_res = knowledge_bot.ask(message=req.message, session_id=req.session_id)
        return ChatResponse(
            session_id=bot_res["session_id"],
            response=bot_res["response"],
            resolved_query=bot_res.get("resolved_query"),
            sources=bot_res.get("sources", [])
        )
    except Exception as e:
        logger.error(f"API Error in /api/chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing chat request: {str(e)}"
        )

@router.post("/chat/clear", response_model=ClearChatResponse, tags=["Task 2"])
async def clear_chat_history(req: ClearChatRequest):
    """
    Task 2: Clears conversation memory for a session ID.
    """
    cleared = memory_manager.clear_history(req.session_id)
    return ClearChatResponse(
        session_id=req.session_id,
        status="cleared" if cleared else "session_not_found"
    )
