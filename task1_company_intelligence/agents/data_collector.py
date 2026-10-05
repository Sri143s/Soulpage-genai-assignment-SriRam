from typing import Dict, Any, List
from task1_company_intelligence.state import CompanyState
from task1_company_intelligence.tools import get_company_news, get_stock_data, get_company_info
from common.logging_config import logger

class DataCollectorAgent:
    """
    Data Collector Agent responsible for invoking tools, retrieving company metrics,
    news, stock, metadata, normalizing data, and updating the LangGraph state.
    """
    def __init__(self):
        pass

    def run(self, state: CompanyState) -> Dict[str, Any]:
        company_name = state.get("company_name", "").strip()
        logger.info(f"--- DATA COLLECTOR AGENT STARTED for '{company_name}' ---")
        
        errors: List[str] = list(state.get("errors", []))
        sources: List[Dict[str, Any]] = list(state.get("sources", []))

        # 1. Retrieve basic company info
        try:
            info_res = get_company_info.invoke({"company_name": company_name})
        except Exception as e:
            logger.error(f"Error in company_info tool: {e}")
            errors.append(f"Company Info Tool Error: {str(e)}")
            info_res = {"company_name": company_name, "description": "Information unavailable."}

        # 2. Retrieve news
        try:
            news_res = get_company_news.invoke({"company_name": company_name})
        except Exception as e:
            logger.error(f"Error in news tool: {e}")
            errors.append(f"News Tool Error: {str(e)}")
            news_res = []

        # 3. Retrieve stock metrics
        try:
            stock_res = get_stock_data.invoke({"company_name": company_name})
        except Exception as e:
            logger.error(f"Error in stock tool: {e}")
            errors.append(f"Stock Tool Error: {str(e)}")
            stock_res = {"symbol": company_name.upper()[:4], "demo_data": True}

        # 4. Extract and collect sources
        for n in news_res:
            if isinstance(n, dict) and "url" in n:
                sources.append({
                    "title": n.get("title", "News Article"),
                    "url": n.get("url", "#"),
                    "source": n.get("source", "News")
                })
        
        if isinstance(info_res, dict) and "sources" in info_res:
            sources.extend(info_res.get("sources", []))

        collected_data = {
            "company_name": company_name,
            "company_info": info_res,
            "news": news_res,
            "stock_data": stock_res,
            "data_collector_status": "COMPLETED"
        }

        logger.info(f"--- DATA COLLECTOR AGENT COMPLETED. Retrieved {len(news_res)} news, stock status: {stock_res.get('symbol')} ---")
        
        return {
            "collected_data": collected_data,
            "news": news_res,
            "stock_data": stock_res,
            "company_info": info_res,
            "sources": sources,
            "errors": errors
        }
