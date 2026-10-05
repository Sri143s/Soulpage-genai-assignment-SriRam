# 🎙️ Technical Interview Walkthrough & Defense Guide

This document provides complete, interview-ready answers to the 20 technical questions regarding the architecture, design patterns, LangGraph orchestration, memory management, and production readiness of this repository.

---

### 1. What problem does the project solve?
This project solves the challenge of extracting actionable business intelligence and delivering grounded conversational knowledge without relying on monolithic, prompt-engineered single-LLM calls. It decomposes complex analysis into a modular, multi-agent pipeline (Task 1) and a memory-aware conversational assistant (Task 2) that grounds answers in external real-time data.

---

### 2. Why did I use LangGraph?
Standard LangChain chains (`LLMChain`, `SequentialChain`) are linear DAGs that struggle with state persistence, complex branching, dynamic tool loops, and cycle control. **LangGraph** models agent workflows as explicit stateful graphs (`StateGraph`). It provides:
- Strongly typed, inspectable state passing between nodes.
- Cyclic execution loops for multi-agent negotiation or validation.
- Built-in checkpointing (`MemorySaver` / `SqliteSaver`) for session persistence.
- Precise control over execution order (Controller → Data Collector → Analyst → Report Formatter).

---

### 3. What is an agent?
An agent is an autonomous software component that pairs an LLM (the reasoning engine) with specific instructions (prompts), tools (external capability APIs), and memory state. Unlike basic LLM calls, agents evaluate context, decide which tools to execute, process tool feedback, and iteratively work towards a defined goal.

---

### 4. What is the Data Collector Agent?
The **Data Collector Agent** (`task1_company_intelligence/agents/data_collector.py`) is responsible for gathering grounding corporate data. It executes three tools:
1. **Company Tool** (`get_company_info`): Retrieves foundational profile, industry, website, and executive leadership metadata.
2. **News Tool** (`get_company_news`): Fetches recent market developments and source URLs.
3. **Stock Tool** (`get_stock_data`): Obtains financial ticker, price, and daily change metrics (with explicit `demo_data` labeling if live market data is unavailable).
It normalizes these results into structured dictionaries and aggregates citation links.

---

### 5. What is the Analyst Agent?
The **Analyst Agent** (`task1_company_intelligence/agents/analyst.py`) receives the structured data collected by the Data Collector Agent. It does **not** execute arbitrary web searches to avoid hallucination. Instead, it synthesizes the collected evidence into four strictly separated categories:
- **FACTS**: Directly verified data points.
- **ANALYSIS**: Market trends and financial trajectory.
- **POTENTIAL RISKS**: Macroeconomic, supply chain, or regulatory threats.
- **POTENTIAL OPPORTUNITIES**: R&D, product expansion, and strategic growth vectors.
It outputs a structured JSON object which is transformed into an executive Markdown report.

---

### 6. How do agents communicate?
In LangGraph, agents do **not** pass unstructured free text strings directly to each other. Communication occurs strictly through shared, strongly typed graph state (`CompanyState`). 
- Node 1 (`data_collector`) populates `state["collected_data"]`, `state["news"]`, `state["stock_data"]`, and `state["sources"]`.
- Node 2 (`analyst`) reads `state` as input, performs LLM reasoning, and writes `state["analysis"]` and `state["final_report"]`.

---

### 7. What is LangGraph state?
LangGraph state is defined using Python's `TypedDict` (`CompanyState` in `task1_company_intelligence/state.py`). It acts as the immutable/versioned data carrier across graph nodes.
```python
class CompanyState(TypedDict, total=False):
    company_name: str
    collected_data: Dict[str, Any]
    news: List[Dict[str, Any]]
    stock_data: Dict[str, Any]
    company_info: Dict[str, Any]
    analysis: Dict[str, Any]
    messages: List[Any]
    errors: List[str]
    sources: List[Dict[str, Any]]
    final_report: str
```

---

### 8. How are tools called?
Tools are built using LangChain's `@tool` decorator or standard typed functions with structured schemas. When an agent or node executes a tool:
1. The tool validates parameters using Pydantic typing.
2. It attempts live external retrieval (e.g., DuckDuckGo, Yahoo Finance, Wikipedia).
3. If an API fails or `DEMO_MODE=true` is active, it catches exceptions gracefully and returns marked fallback data without crashing the pipeline.

---

### 9. How does memory work?
In Task 2, memory is managed by `ConversationMemoryManager` (`task2_knowledge_bot/memory.py`). Modern LangChain message objects (`HumanMessage`, `AIMessage`, `SystemMessage`) are stored in an in-memory dictionary keyed by `session_id`. Deprecated legacy memory classes like `ConversationBufferMemory` were deliberately avoided for future-proof compatibility.

---

### 10. How does Task 2 resolve follow-up questions?
When a user asks a follow-up query containing pronouns (e.g., "Where did he study?" after "Who is the CEO of OpenAI?"):
1. The `_resolve_query_with_context` method inspects previous message history.
2. It detects coreference pronouns ("he", "she", "it", "that company").
3. A zero-temperature LLM step rewrites the query into a standalone entity statement (e.g., "Sam Altman education university").
4. The search tool is invoked with the expanded query, returning precise grounded context.

---

### 11. Why use FastAPI?
FastAPI is a high-performance, asynchronous Python web framework offering:
- Automatic request/response validation via Pydantic models.
- Standardized OpenAPI (Swagger) documentation.
- Decoupled API design allowing Streamlit, React, or mobile clients to consume backend endpoints cleanly.

---

### 12. Why use Streamlit?
Streamlit allows rapid prototyping of interactive data and GenAI interfaces. It native support for `st.chat_input`, `st.chat_message`, `st.status` expanders, and custom metrics makes it ideal for demonstrating agent execution workflows to technical evaluators.

---

### 13. How are hallucinations reduced?
1. **Strict Grounding**: Prompt templates explicitly instruct the LLM to rely *only* on context provided by tools.
2. **Fact/Analysis Separation**: The Analyst Agent must separate raw verified facts from subjective insights.
3. **Structured Citation**: Every output explicitly links back to source URLs provided by Wikipedia or search tools.

---

### 14. How is error handling implemented?
- **Tool Level**: Try-except blocks surround all HTTP requests. Network timeouts or API key errors trigger fallback responses or demo datasets labeled `"demo_data": true`.
- **Node Level**: Errors are appended to `state["errors"]` rather than causing runtime crashes.
- **API Level**: FastAPI handles unhandled exceptions with HTTP 500 error responses and sanitized log outputs.

---

### 15. How would this scale in production?
- **Database Checkpoint**: Replace `MemorySaver` with `PostgresSaver` or Redis for persistent state management across distributed workers.
- **Async Tool Calling**: Use `asyncio.gather()` in `DataCollectorAgent` to execute News, Stock, and Company tools concurrently.
- **Background Queues**: Offload heavy graph execution to Celery / Redis Queue (RQ).

---

### 16. How would I deploy it?
- **Containerization**: Package backend and frontend into Docker containers using a multi-stage Dockerfile.
- **Cloud Hosting**: Deploy FastAPI backend to AWS ECS / GCP Cloud Run / Azure Container Apps.
- **Frontend Hosting**: Deploy Streamlit frontend to Streamlit Community Cloud or AWS Fargate behind a load balancer.

---

### 17. How would I evaluate it?
- **Ragas Framework**: Measure Faithfulness, Answer Relevance, and Context Recall.
- **LangSmith Tracing**: Log latency, token usage, tool invocation latency, and node transition execution times.
- **Human Evaluation**: Conduct blind side-by-side spot checks of generated analyst reports against real market reports.

---

### 18. How could Model Context Protocol (MCP) be added later?
MCP can standardise tool connections. Instead of writing custom Python functions for Stock or Search tools, an MCP client can connect to standardized MCP tool servers (e.g., Brave Search MCP, Postgres MCP, Financial Datasets MCP) via standard JSON-RPC.

---

### 19. How could RAG be added?
To add Retrieval-Augmented Generation (RAG):
1. Ingest corporate annual reports (10-K/10-Q PDFs).
2. Chunk text and store embeddings in a vector store (ChromaDB / Qdrant / FAISS).
3. Add a `VectorSearchTool` to `DataCollectorAgent` to retrieve domain-specific internal documents alongside web search results.

---

### 20. How could Human-in-the-Loop (HITL) be added?
Using LangGraph's `interrupt_before=["analyst"]` feature:
1. The graph pauses after the Data Collector Agent node finishes.
2. The UI renders the collected news and stock metrics for user review.
3. The user approves, edits, or adds extra context before resuming the workflow to execute the Analyst Agent node.
