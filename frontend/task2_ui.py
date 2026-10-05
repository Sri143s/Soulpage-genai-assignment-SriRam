# pyrefly: ignore [missing-import]
import streamlit as st
from task2_knowledge_bot.bot import knowledge_bot
from task2_knowledge_bot.memory import memory_manager

def render_task2_ui(session_id: str):
    st.header("🤖 Task 2: Conversational Knowledge Bot")
    st.caption("Grounded external search + pronoun context resolution across turns")

    # Fetch existing chat history for session
    messages = memory_manager.get_formatted_history(session_id)

    # Render past chat messages
    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Input prompt
    user_input = st.chat_input("Ask a factual question (e.g. 'Who is the CEO of OpenAI?' -> 'Where did he study?')")

    if user_input:
        # Display user query in chat container
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response with spinner
        with st.chat_message("assistant"):
            with st.spinner("Searching knowledge base & resolving conversation context..."):
                res = knowledge_bot.ask(message=user_input, session_id=session_id)
                response_text = res.get("response", "")
                resolved_query = res.get("resolved_query", "")
                sources = res.get("sources", [])

                st.markdown(response_text)

                if resolved_query and resolved_query.lower() != user_input.lower():
                    st.caption(f"🔍 *Context Query Resolution:* `{resolved_query}`")

                if sources:
                    with st.expander("📚 Cited Sources"):
                        for idx, src in enumerate(sources, 1):
                            st.write(f"{idx}. [{src.get('title', 'Source')}]({src.get('url', '#')}) ({src.get('source', 'Web')})")
