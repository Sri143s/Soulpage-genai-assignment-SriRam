import pytest
from task2_knowledge_bot.memory import ConversationMemoryManager
from langchain_core.messages import HumanMessage, AIMessage

def test_memory_manager_add_and_get():
    mem = ConversationMemoryManager()
    session_id = "test_sess_1"
    
    mem.add_user_message(session_id, "Who is the CEO of OpenAI?")
    mem.add_ai_message(session_id, "The CEO of OpenAI is Sam Altman.")

    msgs = mem.get_messages(session_id)
    assert len(msgs) == 2
    assert isinstance(msgs[0], HumanMessage)
    assert msgs[0].content == "Who is the CEO of OpenAI?"
    assert isinstance(msgs[1], AIMessage)
    assert msgs[1].content == "The CEO of OpenAI is Sam Altman."

def test_memory_formatted_history():
    mem = ConversationMemoryManager()
    session_id = "test_sess_2"
    mem.add_user_message(session_id, "Hello")
    mem.add_ai_message(session_id, "Hi there")

    formatted = mem.get_formatted_history(session_id)
    assert len(formatted) == 2
    assert formatted[0] == {"role": "user", "content": "Hello"}
    assert formatted[1] == {"role": "assistant", "content": "Hi there"}

def test_memory_clear():
    mem = ConversationMemoryManager()
    session_id = "test_sess_3"
    mem.add_user_message(session_id, "Test clear")
    assert len(mem.get_messages(session_id)) == 1

    cleared = mem.clear_history(session_id)
    assert cleared is True
    assert len(mem.get_messages(session_id)) == 0
