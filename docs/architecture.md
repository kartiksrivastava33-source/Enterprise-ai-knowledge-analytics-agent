
flowchart TD
    U["User"] --> FE["Streamlit Frontend"]
    FE --> API["FastAPI Backend"]
    API --> LG["LangGraph Agent Workflow"]

    LG --> R{"Question Router"}

    R -->|Document question| RAG["Document Retrieval"]
    R -->|Analytics question| AN["Analytics Tool"]
    R -->|Combined question| BOTH["Document + Analytics"]

    RAG --> FAISS[("FAISS Vector Database")]
    FAISS --> PDF["PDF Documents"]

    AN --> DF["Pandas Analytics"]
    BOTH --> FAISS
    BOTH --> DF

    DF --> CSV["Superstore Sales CSV"]

    RAG --> LLM["Gemini LLM"]
    AN --> LLM
    BOTH --> LLM

    LLM --> OUT["Structured Response"]
    OUT --> API

    LG <--> MEM[("SQLite Conversation Memory")]

    API --> FE
