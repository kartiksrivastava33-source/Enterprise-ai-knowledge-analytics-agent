# Enterprise AI Knowledge & Analytics Agent

An AI-powered business assistant that combines enterprise document retrieval and structured business analytics through a conversational interface.

## Overview

The Enterprise AI Knowledge & Analytics Agent allows users to ask natural-language questions about company documents and business sales data.

It uses Retrieval-Augmented Generation (RAG) to retrieve relevant information from PDF documents and analytics tools to answer questions about structured sales data.

A LangGraph workflow routes questions to the appropriate capability and supports combined document and analytics queries.

## Key Features

- **Document Q&A:** Retrieve information from PDF documents using semantic search.
- **RAG with citations:** Generate answers grounded in retrieved document content with source and page references.
- **Business analytics:** Analyze sales data by region, category and top-performing products.
- **Intelligent routing:** Route questions to document retrieval, analytics or both.
- **Conversational memory:** Maintain conversation history using LangGraph and SQLite.
- **Structured responses:** Use Pydantic to produce answers, sources and insights.
- **REST API:** Expose the agent through FastAPI.
- **Interactive interface:** Chat with the agent through Streamlit.
- **Containerization:** Package the application using Docker and Docker Compose.

## Architecture

## Architecture

See [Architecture Diagram](docs/architecture.md).

The application follows this workflow:

1. User submits a question through Streamlit.
2. Streamlit sends the request to the FastAPI backend.
3. LangGraph routes the question to the appropriate workflow.
4. The document retrieval tool searches the FAISS vector database, or the analytics tool processes the sales dataset.
5. Retrieved information is passed to the language model.
6. The agent generates a structured response.
7. The response is returned to the frontend.

## Technology Stack

| Component | Technology |
|---|---|
| Language | Python |
| LLM | Google Gemini |
| Agent workflow | LangGraph |
| LLM framework | LangChain |
| Embeddings | HuggingFace Sentence Transformers |
| Vector database | FAISS |
| Data processing | Pandas |
| API | FastAPI |
| Validation | Pydantic |
| Frontend | Streamlit |
| Conversation memory | SQLite |
| Testing | Pytest |
| Containerization | Docker, Docker Compose |

## Data Sources

### Documents
PDF documents are processed, split into chunks, embedded and stored in FAISS for semantic retrieval.

### Sales Analytics
The project uses the Sample Superstore sales dataset.

Available analyses include:
- Sales by region
- Sales by product category
- Top-performing products

**Note:** The dataset used in this project does not contain Profit or Quantity columns, so those metrics are not included.

## Project Structure

```text
enterprise-genai/
│
├── agent/
│   └── workflow.py
│
├── data/
│   ├── documents/
│   ├── vector_db/
│   └── sales_data.csv
│
├── tests/
│   └── test_api.py
│
├── app.py
├── frontend.py
├── main.ipynb
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── .gitignore
└── README.md
```

## Run Locally

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd enterprise-genai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file:

```text
GEMINI_API_KEY=your_api_key
```

### 5. Start the backend

```bash
uvicorn app:app --reload
```

### 6. Start the frontend

In another terminal:

```bash
streamlit run frontend.py
```

## Run with Docker

Build and start both services:

```bash
docker compose up --build
```

Access the application:

- Streamlit: http://localhost:8501
- FastAPI documentation: http://localhost:8000/docs

## Run Tests

```bash
python -m pytest tests/ -v
```

## Future Improvements

- Cloud deployment
- Improved retrieval evaluation
- More structured business datasets
- User authentication and access control

## Author

Kartik Srivastava

Electronics and Computer Engineering Student  
Thapar Institute of Engineering and Technology
