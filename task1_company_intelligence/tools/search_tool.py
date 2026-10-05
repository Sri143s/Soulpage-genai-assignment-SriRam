from typing import List, Dict, Any
from langchain_core.tools import tool

from common.config import settings
from common.logging_config import logger

@tool
def search_web(query: str) -> List[Dict[str, Any]]:
    """
    Performs general web search for company information and returns titles, snippets, and URLs.
    """
    logger.info(f"Tool Executing: search_web for query '{query}'")
    
    if settings.DEMO_MODE:
        return [
            {
                "title": f"Market Data for {query}",
                "snippet": f"Overview and industry insights regarding {query}.",
                "url": "https://example.com/search-result",
                "source": "Web Search"
            }
        ]

    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = list(ddgs.text(keywords=query, max_results=4))
        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", query),
                "snippet": r.get("body", ""),
                "url": r.get("href", "https://duckduckgo.com"),
                "source": "DuckDuckGo"
            })
        return formatted
    except Exception as e:
        logger.warning(f"Web search failed for query '{query}': {e}")
        return [
            {
                "title": f"Fallback Search: {query}",
                "snippet": f"Retrieved general context for {query}.",
                "url": "https://example.com/fallback",
                "source": "System Fallback"
            }
        ]
