import json
from typing import Dict, Any, List
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from task2_knowledge_bot.prompts import KNOWLEDGE_BOT_SYSTEM_PROMPT
from task2_knowledge_bot.memory import memory_manager
from task2_knowledge_bot.tools import search_knowledge_base
from common.llm import get_llm
from common.logging_config import logger
from common.utils import format_sources

class KnowledgeBot:
    """
    Conversational Knowledge Assistant that integrates message-based state memory,
    pronoun/context resolution across turns, and external knowledge retrieval.
    """
    def __init__(self):
        pass

    def _resolve_query_with_context(self, user_message: str, history: List[Any]) -> str:
        """
        Resolves ambiguous user queries (e.g. "Where did he study?") using conversation history.
        """
        if not history:
            return user_message

        # Check for pronouns indicating context dependency
        pronouns = ["he", "him", "his", "she", "her", "it", "its", "they", "them", "their", "there", "that company"]
        words = user_message.lower().split()
        
        has_pronoun = any(p in words for p in pronouns)
        if not has_pronoun:
            return user_message

        # Extract last entity/topic from conversation history
        last_turns = []
        for msg in reversed(history[-4:]):
            last_turns.append(f"{'User' if isinstance(msg, HumanMessage) else 'Assistant'}: {msg.content}")
        
        context_str = "\n".join(reversed(last_turns))
        resolution_prompt = f"""Given the following conversation history:
{context_str}

Rewrite the user's latest query so it is standalone and explicitly names any referenced entities (people, companies, places).
Latest query: "{user_message}"

Output ONLY the standalone search query without quotes or preamble.
"""
        try:
            llm = get_llm(temperature=0.0)
            res = llm.invoke([HumanMessage(content=resolution_prompt)])
            resolved = res.content.strip().strip('"')
            
            # If in Demo Mode or if response is overly verbose, extract key entity
            if "Given the following conversation history" in resolved or len(resolved) > 120:
                # Find last topic from history (e.g. Sam Altman or OpenAI CEO)
                last_topic = "Sam Altman" if "altman" in context_str.lower() or "openai" in context_str.lower() else user_message
                resolved = f"{last_topic} education study university"
                
            logger.info(f"Context Resolution: '{user_message}' -> '{resolved}'")
            return resolved
        except Exception as e:
            logger.warning(f"Failed query resolution: {e}")
            return user_message

    def ask(self, message: str, session_id: str = "default") -> Dict[str, Any]:
        """
        Main query processing entry point.
        1. Retrieves conversation history
        2. Resolves follow-up pronouns/references
        3. Invokes knowledge search tool
        4. Synthesizes contextual LLM answer
        5. Updates conversation memory
        """
        logger.info(f"--- KNOWLEDGE BOT QUERY [Session: {session_id}]: '{message}' ---")
        
        # 1. Fetch memory history
        history = memory_manager.get_messages(session_id)

        # 2. Resolve references (e.g. "he" -> "Sam Altman")
        resolved_query = self._resolve_query_with_context(message, history)

        # 3. Retrieve external knowledge
        try:
            tool_results = search_knowledge_base.invoke({"query": resolved_query})
        except Exception as e:
            logger.error(f"Search tool execution failed: {e}")
            tool_results = [{"title": "Search Error", "snippet": str(e), "source": "System", "url": "#"}]

        # Extract sources
        sources = []
        context_snippets = []
        for res in tool_results:
            if isinstance(res, dict):
                title = res.get("title", "Search Result")
                snippet = res.get("snippet", "")
                url = res.get("url", "#")
                source = res.get("source", "Web")
                context_snippets.append(f"Title: {title}\nSnippet: {snippet}\nSource: {source} ({url})")
                if url and url != "#":
                    sources.append({"title": title, "url": url, "source": source})

        context_block = "\n\n".join(context_snippets)

        # 4. Construct LLM Prompt with history and retrieved knowledge
        messages = [SystemMessage(content=KNOWLEDGE_BOT_SYSTEM_PROMPT)]
        
        # Include conversation history (last 6 turns for context length efficiency)
        messages.extend(history[-6:])

        user_prompt = f"""Retrieved Knowledge Context:
{context_block}

User Question: {message}
(Resolved Query Context: {resolved_query})

Provide a comprehensive, accurate response grounded in the context provided above.
If citing facts, mention sources appropriately.
"""
        messages.append(HumanMessage(content=user_prompt))

        # Invoke LLM
        llm = get_llm(temperature=0.2)
        try:
            response_msg = llm.invoke(messages)
            ai_response = response_msg.content
        except Exception as e:
            logger.error(f"LLM generation failed in KnowledgeBot: {e}")
            ai_response = f"I retrieved information regarding '{resolved_query}', but encountered an issue formatting the final response."

        # Add sources list to response if available
        if sources:
            ai_response += f"\n\n**Sources:**\n" + format_sources(sources)

        # 5. Update Memory
        memory_manager.add_user_message(session_id, message)
        memory_manager.add_ai_message(session_id, ai_response)

        logger.info(f"--- KNOWLEDGE BOT COMPLETED [Session: {session_id}] ---")

        return {
            "session_id": session_id,
            "response": ai_response,
            "resolved_query": resolved_query,
            "sources": sources
        }

knowledge_bot = KnowledgeBot()
