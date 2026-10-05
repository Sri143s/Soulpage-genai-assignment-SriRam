from typing import List, Dict, Any
from langchain_core.tools import tool

from common.config import settings
from common.logging_config import logger

@tool
def search_knowledge_base(query: str) -> List[Dict[str, Any]]:
    """
    Searches Wikipedia and public knowledge engines for factual information on entities, people, concepts, and history.
    """
    logger.info(f"Knowledge Search Tool Executing for query: '{query}'")
    
    results: List[Dict[str, Any]] = []

    if settings.DEMO_MODE:
        q_lower = query.lower()
        if "ceo" in q_lower or "openai" in q_lower:
            return [
                {
                    "title": "Sam Altman",
                    "snippet": "Samuel Harris Altman (born April 22, 1985) is an American entrepreneur and investor who is the chief executive officer (CEO) of OpenAI.",
                    "source": "Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Sam_Altman"
                }
            ]
        elif "study" in q_lower or "education" in q_lower or "university" in q_lower or "altman" in q_lower:
            return [
                {
                    "title": "Sam Altman Education",
                    "snippet": "Altman attended Stanford University to study computer science, but dropped out after one year in 2005 without earning a degree to co-found Loopt.",
                    "source": "Wikipedia",
                    "url": "https://en.wikipedia.org/wiki/Sam_Altman#Early_life_and_education"
                }
            ]
        else:
            return [
                {
                    "title": f"Factual Overview: {query}",
                    "snippet": f"Knowledge base entry providing contextual information regarding {query}.",
                    "source": "Verified Knowledge Base",
                    "url": "https://example.com/knowledge"
                }
            ]

    # Live search attempt via Wikipedia first
    try:
        import wikipedia
        wiki_summary = wikipedia.summary(query, sentences=3)
        wiki_page = wikipedia.page(query, auto_suggest=True)
        results.append({
            "title": wiki_page.title,
            "snippet": wiki_summary,
            "source": "Wikipedia",
            "url": wiki_page.url
        })
    except Exception as e:
        logger.warning(f"Wikipedia search failed for '{query}': {e}")

    # Supplementary DuckDuckGo search
    try:
        from duckduckgo_search import DDGS
        ddgs = DDGS()
        ddg_results = list(ddgs.text(keywords=query, max_results=3))
        for r in ddg_results:
            results.append({
                "title": r.get("title", query),
                "snippet": r.get("body", ""),
                "source": "DuckDuckGo",
                "url": r.get("href", "#")
            })
    except Exception as e:
        logger.warning(f"DuckDuckGo search failed for '{query}': {e}")

    if not results:
        results.append({
            "title": f"No Results Found for {query}",
            "snippet": "No definitive factual records retrieved for the query.",
            "source": "System",
            "url": "#"
        })

    return results
