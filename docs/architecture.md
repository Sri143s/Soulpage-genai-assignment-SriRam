# 🏗️ Architecture Documentation

## Overview

The **Soulpage GenAI Assignment Repository** is designed with a clean, decoupled architecture separating LLM provider logic, multi-agent orchestration, state persistence, tools, backend APIs, and frontend presentation.

---

## 1. System Architecture Overview

```mermaid
flowchart TD
    subgraph Client Layer
        A[User Browser / Streamlit UI]
    end

    subgraph API Layer
        B[FastAPI Server]
        B1[GET /api/health]
        B2[POST /api/company/analyze]
        B3[POST /api/chat]
        B4[POST /api/chat/clear]
    end

    subgraph Orchestration Layer Task 1
        C[LangGraph Controller Node]
        D[Data Collector Agent]
        E[News Tool]
        F[Stock Tool]
        G[Company Tool]
        H[Search Tool]
        I[Typed State: CompanyState]
        J[Analyst Agent]
        K[Final Report Formatter]
    end

    subgraph Memory & Search Task 2
        L[Conversation Memory Manager]
        M[Knowledge Search Tool]
        N[LLM Provider Abstraction]
    end

    A -->|HTTP Requests| B
    B -->|Task 1 Analysis| C
    C --> D
    D --> E & F & G & H
    E & F & G & H --> I
    I --> J
    J --> K
    K --> B

    B -->|Task 2 Chat| L
    L --> M
    M --> N
    N --> B
```

---

## 2. Task 1: Multi-Agent Company Intelligence Pipeline

```mermaid
flowchart TD
    START([START]) --> Controller[Controller Node]
    Controller --> Collector[Data Collector Agent]
    
    subgraph Tool Execution Group
        Collector -->|Invoke| News[News Tool]
        Collector -->|Invoke| Stock[Stock Tool]
        Collector -->|Invoke| Company[Company Info Tool]
    end
    
    News --> State[(CompanyState)]
    Stock --> State
    Company --> State
    
    State --> Analyst[Analyst Agent]
    Analyst --> Report[Final Report Synthesis]
    Report --> END([END])
```

### Key Workflow Steps:
1. **Controller Node**: Validates input string, assigns session ID, initializes `CompanyState`.
2. **Data Collector Agent**: Concurrently executes `get_company_info`, `get_company_news`, and `get_stock_data`. Populates collected data and preserves source URLs.
3. **Analyst Agent**: Evaluates state, categorizes Facts, Analysis, Risks, and Opportunities using `AnalystPrompt`, and outputs structured markdown report.

---

## 3. Task 2: Conversational Knowledge Bot Architecture

```mermaid
flowchart TD
    User[User Input] --> Streamlit[Streamlit Chat UI]
    Streamlit --> FastAPI[FastAPI Backend]
    FastAPI --> Bot[Knowledge Bot Manager]
    Bot --> Memory[Conversation Memory Manager]
    
    subgraph Context Resolution & Retrieval
        Memory --> QueryRes[Pronoun Query Resolver]
        QueryRes --> SearchTool[Wikipedia & DDG Tool]
    end
    
    SearchTool --> LLM[LLM Factory Groq/OpenAI/Demo]
    LLM --> Response[Contextual Response + Sources]
    Response --> User
```

---

## 4. Provider Abstraction & Fallback Pattern

The application implements a provider abstraction layer (`common/llm.py`):

```
                   +-----------------------+
                   |  common.llm.get_llm() |
                   +-----------+-----------+
                               |
         +---------------------+---------------------+
         |                     |                     |
         v                     v                     v
   +-----------+         +-----------+         +-----------+
   | ChatGroq  |         |ChatOpenAI |         | DemoModel |
   +-----------+         +-----------+         +-----------+
   (If Groq Key)         (If OpenAI Key)       (Fallback Mode)
```

If API keys are omitted or `DEMO_MODE=true`, the system dynamically routes calls to `DemoChatModel`, ensuring that **all tests and demonstrations execute without runtime errors or crashes**.
