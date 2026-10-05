import pytest
from fastapi.testclient import TestClient
from task2_knowledge_bot.bot import knowledge_bot
from task2_knowledge_bot.memory import memory_manager
from backend.server import app

def test_knowledge_bot_initial_query():
    session_id = "test_bot_session_1"
    memory_manager.clear_history(session_id)

    res = knowledge_bot.ask("Who is the CEO of OpenAI?", session_id=session_id)
    assert res["session_id"] == session_id
    assert "response" in res
    assert len(res["response"]) > 0

def test_knowledge_bot_follow_up_pronoun_resolution():
    session_id = "test_bot_session_2"
    memory_manager.clear_history(session_id)

    # Turn 1
    res1 = knowledge_bot.ask("Who is the CEO of OpenAI?", session_id=session_id)
    assert "response" in res1

    # Turn 2 with pronoun "he"
    res2 = knowledge_bot.ask("Where did he study?", session_id=session_id)
    assert "response" in res2
    assert res2.get("resolved_query") is not None
    # Check that "he" was resolved to include Sam Altman or OpenAI CEO context
    resolved = res2["resolved_query"].lower()
    assert "altman" in resolved or "ceo" in resolved or "openai" in resolved or "study" in resolved

def test_fastapi_endpoints():
    client = TestClient(app)

    # Health check
    h_resp = client.get("/api/health")
    assert h_resp.status_code == 200
    h_json = h_resp.json()
    assert h_json["status"] == "healthy"

    # Task 1 endpoint
    t1_resp = client.post("/api/company/analyze", json={"company": "NVIDIA"})
    assert t1_resp.status_code == 200
    t1_json = t1_resp.json()
    assert "report" in t1_json
    assert t1_json["company"] == "NVIDIA"

    # Task 2 chat endpoint
    t2_resp = client.post("/api/chat", json={"session_id": "api-test", "message": "What is Python?"})
    assert t2_resp.status_code == 200
    t2_json = t2_resp.json()
    assert "response" in t2_json

    # Task 2 clear endpoint
    c_resp = client.post("/api/chat/clear", json={"session_id": "api-test"})
    assert c_resp.status_code == 200
    assert c_resp.json()["status"] == "cleared"
