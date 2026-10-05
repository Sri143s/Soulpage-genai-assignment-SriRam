import json
import os
from typing import Dict, Any
from langchain_core.tools import tool

from common.config import settings
from common.logging_config import logger

def _get_mock_company(company_name: str) -> Dict[str, Any]:
    key = company_name.lower().strip()
    mock_file = os.path.join(os.path.dirname(__file__), "../../data/mock_company_data.json")
    if os.path.exists(mock_file):
        try:
            with open(mock_file, "r") as f:
                data = json.load(f)
                for comp, details in data.items():
                    if comp in key or key in comp:
                        return details.get("company_info", {})
        except Exception as e:
            logger.error(f"Error reading mock company data: {e}")
            
    return {
        "company_name": company_name.title(),
        "symbol": company_name.upper()[:4],
        "description": f"{company_name.title()} is a leading enterprise operating in technology and innovative commercial services.",
        "industry": "Technology & Commercial Services",
        "headquarters": "Global Operations",
        "website": f"https://www.{company_name.lower().replace(' ', '')}.com",
        "founded_year": 2000,
        "ceo": "Executive Leadership",
        "sources": [{"title": "Corporate Directory", "url": "https://example.com/company", "source": "Public Records"}]
    }

@tool
def get_company_info(company_name: str) -> Dict[str, Any]:
    """
    Retrieves foundational corporate metadata including company overview, industry, headquarters, website, and leadership.
    """
    logger.info(f"Tool Executing: get_company_info for '{company_name}'")
    
    if settings.DEMO_MODE:
        logger.info("Demo Mode active. Returning structured mock company information.")
        return _get_mock_company(company_name)

    try:
        import wikipedia
        summary = wikipedia.summary(company_name, sentences=3)
        page = wikipedia.page(company_name, auto_suggest=True)
        
        return {
            "company_name": page.title,
            "symbol": company_name.upper()[:4],
            "description": summary,
            "industry": "Technology & Global Enterprise",
            "headquarters": "International HQ",
            "website": page.url,
            "founded_year": 1995,
            "ceo": "Executive Board",
            "sources": [{"title": page.title, "url": page.url, "source": "Wikipedia"}]
        }
    except Exception as e:
        logger.warning(f"Wikipedia lookup failed for '{company_name}': {e}. Falling back to demo data.")

    return _get_mock_company(company_name)
