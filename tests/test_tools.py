import pytest
from task1_company_intelligence.tools.news_tool import get_company_news
from task1_company_intelligence.tools.stock_tool import get_stock_data
from task1_company_intelligence.tools.company_tool import get_company_info
from task1_company_intelligence.tools.search_tool import search_web
from task2_knowledge_bot.tools import search_knowledge_base

def test_news_tool():
    res = get_company_news.invoke({"company_name": "NVIDIA"})
    assert isinstance(res, list)
    assert len(res) > 0
    first = res[0]
    assert "title" in first
    assert "summary" in first
    assert "url" in first

def test_stock_tool():
    res = get_stock_data.invoke({"company_name": "Microsoft"})
    assert isinstance(res, dict)
    assert "symbol" in res
    assert "price" in res
    assert "demo_data" in res
    assert res["demo_data"] is True or isinstance(res["demo_data"], bool)

def test_company_tool():
    res = get_company_info.invoke({"company_name": "Apple"})
    assert isinstance(res, dict)
    assert "company_name" in res
    assert "description" in res
    assert "industry" in res

def test_search_tool():
    res = search_web.invoke({"query": "NVIDIA revenue 2026"})
    assert isinstance(res, list)
    assert len(res) > 0

def test_knowledge_search_tool():
    res = search_knowledge_base.invoke({"query": "OpenAI CEO"})
    assert isinstance(res, list)
    assert len(res) > 0
    assert "title" in res[0]
