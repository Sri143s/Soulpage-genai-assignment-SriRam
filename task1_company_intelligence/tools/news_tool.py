import json
import os
from typing import List, Dict, Any
from langchain_core.tools import tool

from common.config import settings
from common.logging_config import logger

def _get_mock_news(company_name: str) -> List[Dict[str, Any]]:
    key = company_name.lower().strip()
    mock_file = os.path.join(os.path.dirname(__file__), "../../data/mock_company_data.json")
    if os.path.exists(mock_file):
        try:
            with open(mock_file, "r") as f:
                data = json.load(f)
                for comp, details in data.items():
                    if comp in key or key in comp:
                        return details.get("news", [])
        except Exception as e:
            logger.error(f"Error reading mock news data: {e}")
            
    # Generic mock news fallback
    return [
        {
            "title": f"{company_name} Expands Global AI & Technology Initiatives",
            "summary": f"{company_name} announced strategic investments to accelerate technological capabilities and enterprise product scaling.",
            "source": "Tech Standard",
            "url": f"https://example.com/news/{company_name.lower()}-expansion",
            "published_at": "2026-10-01"
        },
        {
            "title": f"Market Analysts Review {company_name} Quarterly Outlook",
            "summary": f"Industry analysts highlight strong operational fundamentals and resilient market positioning for {company_name}.",
            "source": "Global Business Review",
            "url": f"https://example.com/news/{company_name.lower()}-outlook",
            "published_at": "2026-09-28"
        }
    ]

@tool
def get_company_news(company_name: str) -> List[Dict[str, Any]]:
    """
    Retrieves recent news articles related to the specified company.
    Returns a list of structured news items with title, summary, source, url, and published_at.
    """
    logger.info(f"Tool Executing: get_company_news for '{company_name}'")
    
    if settings.DEMO_MODE:
        logger.info("Demo Mode active. Returning structured mock news.")
        return _get_mock_news(company_name)

    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        results = list(ddgs.news(keywords=f"{company_name} company news", max_results=5))
        if results:
            formatted_news = []
            for item in results:
                formatted_news.append({
                    "title": item.get("title", f"{company_name} News"),
                    "summary": item.get("body", "No summary available."),
                    "source": item.get("source", "DuckDuckGo News"),
                    "url": item.get("url", "https://news.google.com"),
                    "published_at": item.get("date", "Recent")
                })
            logger.info(f"Successfully retrieved {len(formatted_news)} news items for {company_name}.")
            return formatted_news
    except Exception as e:
        logger.warning(f"Live news search failed for '{company_name}': {e}. Falling back to demo data.")

    return _get_mock_news(company_name)
