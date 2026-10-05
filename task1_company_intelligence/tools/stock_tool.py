import json
import os
import datetime
from typing import Dict, Any
from langchain_core.tools import tool

from common.config import settings
from common.logging_config import logger

def _get_mock_stock(company_name: str) -> Dict[str, Any]:
    key = company_name.lower().strip()
    mock_file = os.path.join(os.path.dirname(__file__), "../../data/mock_company_data.json")
    if os.path.exists(mock_file):
        try:
            with open(mock_file, "r") as f:
                data = json.load(f)
                for comp, details in data.items():
                    if comp in key or key in comp:
                        return details.get("stock_data", {})
        except Exception as e:
            logger.error(f"Error reading mock stock data: {e}")
            
    return {
        "symbol": company_name.upper()[:4],
        "price": 150.00,
        "change": 1.50,
        "change_percent": 1.00,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "currency": "USD",
        "demo_data": True,
        "disclaimer": "DEMO DATA — NOT LIVE MARKET DATA"
    }

@tool
def get_stock_data(company_name: str) -> Dict[str, Any]:
    """
    Retrieves stock data for a given company symbol or name.
    Returns ticker symbol, current price, net change, percentage change, and demo data status.
    """
    logger.info(f"Tool Executing: get_stock_data for '{company_name}'")
    
    if settings.DEMO_MODE:
        logger.info("Demo Mode active. Returning marked mock stock data.")
        return _get_mock_stock(company_name)

    # Attempt fetching real stock info via free finance web endpoint or fallback
    try:
        import httpx
        # Free public stock API endpoint (e.g. query quote endpoint or yfinance fallback)
        symbol = company_name.upper()[:4]
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = httpx.get(url, headers=headers, timeout=4.0)
        if resp.status_code == 200:
            result = resp.json()["chart"]["result"][0]
            meta = result["meta"]
            price = meta.get("regularMarketPrice", 100.0)
            prev = meta.get("chartPreviousClose", price)
            change = round(price - prev, 2)
            pct = round((change / prev) * 100, 2) if prev else 0.0
            
            return {
                "symbol": meta.get("symbol", symbol),
                "price": price,
                "change": change,
                "change_percent": pct,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "currency": meta.get("currency", "USD"),
                "demo_data": False,
                "disclaimer": "LIVE MARKET DATA"
            }
    except Exception as e:
        logger.warning(f"Live stock fetch failed for '{company_name}': {e}. Switching to DEMO MODE stock data.")

    return _get_mock_stock(company_name)
