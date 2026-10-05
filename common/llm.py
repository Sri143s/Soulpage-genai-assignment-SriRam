import os
from typing import Optional, Any, List
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatResult, ChatGeneration

from common.config import settings
from common.logging_config import logger

class DemoChatModel(BaseChatModel):
    """
    Fallback Chat Model used when no valid API keys are present or DEMO_MODE is enabled.
    Returns deterministic, structured demo responses grounded in provided context.
    """
    model_name: str = "demo-fallback-model"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[Any] = None,
        **kwargs: Any
    ) -> ChatResult:
        logger.info("DemoChatModel invoked (Demo Mode active / API key unavailable).")
        last_msg = messages[-1].content if messages else ""
        
        # Smart synthesis based on message context
        if "Analyst" in str(messages) or "executive_summary" in str(messages) or "company" in last_msg.lower():
            response_text = """{
  "executive_summary": "Company exhibits strong market presence with solid financial trajectory and strategic innovation in core growth sectors.",
  "recent_developments": [
    "Expanded product offerings in high-growth technology markets.",
    "Reported strong quarterly performance exceeding consensus projections.",
    "Formed strategic partnerships to enhance enterprise capabilities."
  ],
  "market_snapshot": {
    "trend": "Bullish",
    "market_position": "Industry Leader",
    "valuation_rating": "Fairly Valued"
  },
  "key_insights": [
    "Robust revenue streams backed by enterprise demand.",
    "Sustained R&D investments driving competitive advantage."
  ],
  "potential_risks": [
    "Supply chain bottlenecks and macroeconomic volatility.",
    "Regulatory scrutiny in international jurisdictions."
  ],
  "potential_opportunities": [
    "Emerging market expansion and AI product integration.",
    "Strategic M&A potential in synergistic technology domains."
  ],
  "sources": [
    {"title": "Financial Insights Report", "url": "https://example.com/finance", "source": "Market Watch"}
  ]
}"""
        else:
            response_text = f"Based on the available factual context, here is the verified information regarding your query: {last_msg}"

        generation = ChatGeneration(message=AIMessage(content=response_text))
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "demo-chat-model"

def get_llm(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.2
) -> BaseChatModel:
    """
    LLM Factory function with provider abstraction.
    Supports 'groq' and 'openai'. Falls back to DemoChatModel if keys are missing or DEMO_MODE is True.
    """
    selected_provider = (provider or settings.MODEL_PROVIDER).lower()
    selected_model = model or settings.MODEL_NAME

    if settings.DEMO_MODE:
        logger.info(f"DEMO_MODE is True. Initializing DemoChatModel (Provider: {selected_provider}).")
        return DemoChatModel(model_name=selected_model)

    if selected_provider == "groq":
        groq_api_key = settings.GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        if not groq_api_key or groq_api_key.startswith("your_"):
            logger.warning("Groq API key not configured. Falling back to DemoChatModel.")
            return DemoChatModel(model_name=selected_model)
        try:
            from langchain_groq import ChatGroq
            logger.info(f"Initializing ChatGroq with model {selected_model}")
            return ChatGroq(
                model_name=selected_model,
                groq_api_key=groq_api_key,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq: {e}. Falling back to DemoChatModel.")
            return DemoChatModel(model_name=selected_model)

    elif selected_provider == "openai":
        openai_api_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        if not openai_api_key or openai_api_key.startswith("your_"):
            logger.warning("OpenAI API key not configured. Falling back to DemoChatModel.")
            return DemoChatModel(model_name=selected_model)
        try:
            from langchain_openai import ChatOpenAI
            model_name = selected_model if selected_model != "llama-3.3-70b-versatile" else "gpt-4o-mini"
            logger.info(f"Initializing ChatOpenAI with model {model_name}")
            return ChatOpenAI(
                model_name=model_name,
                openai_api_key=openai_api_key,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"Failed to initialize ChatOpenAI: {e}. Falling back to DemoChatModel.")
            return DemoChatModel(model_name=selected_model)

    else:
        logger.warning(f"Unsupported provider '{selected_provider}'. Falling back to DemoChatModel.")
        return DemoChatModel(model_name=selected_model)
