from typing import List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from common.logging_config import logger

class ConversationMemoryManager:
    """
    Session-level conversation memory manager using modern LangChain message abstractions
    (HumanMessage, AIMessage, SystemMessage). Avoids deprecated legacy memory classes.
    """
    def __init__(self):
        # In-memory store keyed by session_id
        self._store: Dict[str, List[BaseMessage]] = {}

    def get_messages(self, session_id: str) -> List[BaseMessage]:
        """
        Retrieves the full message history for a given session_id.
        """
        return self._store.get(session_id, [])

    def add_user_message(self, session_id: str, content: str) -> None:
        """
        Appends a HumanMessage to the session history.
        """
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append(HumanMessage(content=content))
        logger.info(f"Added HumanMessage to session '{session_id}'. Total messages: {len(self._store[session_id])}")

    def add_ai_message(self, session_id: str, content: str) -> None:
        """
        Appends an AIMessage to the session history.
        """
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append(AIMessage(content=content))
        logger.info(f"Added AIMessage to session '{session_id}'. Total messages: {len(self._store[session_id])}")

    def clear_history(self, session_id: str) -> bool:
        """
        Clears message history for a session_id.
        """
        if session_id in self._store:
            del self._store[session_id]
            logger.info(f"Cleared conversation history for session '{session_id}'.")
            return True
        return False

    def get_formatted_history(self, session_id: str) -> List[Dict[str, str]]:
        """
        Returns history formatted for UI rendering (e.g. Streamlit chat).
        """
        formatted = []
        for msg in self.get_messages(session_id):
            if isinstance(msg, HumanMessage):
                formatted.append({"role": "user", "content": msg.content})
            elif isinstance(msg, AIMessage):
                formatted.append({"role": "assistant", "content": msg.content})
        return formatted

# Global memory manager instance
memory_manager = ConversationMemoryManager()
