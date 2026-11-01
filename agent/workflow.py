
import os
import sqlite3
import pandas as pd

from pathlib import Path
from dotenv import load_dotenv
from typing import TypedDict

from pydantic import BaseModel

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.tools import tool

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver


# =====================================
# 1. PATHS AND ENVIRONMENT
# =====================================

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")


# =====================================
# 2. GEMINI MODEL
# =====================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=api_key
)


def get_text(response):
    content = response.content

    if isinstance(content, list):
        return "".join(
            item["text"]
            for item in content
            if isinstance(item, dict) and item.get("type") == "text"
        )

    return content


# =====================================
# 3. FAISS AND EMBEDDINGS
# =====================================

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vector_db = FAISS.load_local(
    str(BASE_DIR / "data" / "vector_db"),
    embeddings,
    allow_dangerous_deserialization=True
)

retriever = vector_db.as_retriever(
    search_type="mmr",
    search_kwargs={
        "k": 4,
        "fetch_k": 10,
        "lambda_mult": 0.5
    }
)


# =====================================
# 4. SALES DATA
# =====================================

df = pd.read_csv(BASE_DIR / "data" / "train.csv")

df = df.drop(columns=["Row ID"], errors="ignore")

df["Order Date"] = pd.to_datetime(
    df["Order Date"], dayfirst=True
)

df["Ship Date"] = pd.to_datetime(
    df["Ship Date"], dayfirst=True
)

df["Postal Code"] = df["Postal Code"].fillna(0)

df["Year"] = df["Order Date"].dt.year
df["Month"] = df["Order Date"].dt.month


# =====================================
# 5. ANALYTICS FUNCTIONS
# =====================================

def regional_analysis():
    result = df.groupby("Region")["Sales"].sum()
    return result.sort_values(ascending=False).to_dict()


def category_analysis():
    result = df.groupby("Category")["Sales"].sum()
    return result.sort_values(ascending=False).to_dict()


def top_products(n=5):
    result = df.groupby("Product Name")["Sales"].sum()
    return result.sort_values(ascending=False).head(n).to_dict()


# =====================================
# 6. LANGCHAIN TOOLS
# =====================================

@tool
def search_documents(question: str) -> str:
    """Search company documents and return relevant passages with source pages."""

    results = retriever.invoke(question)

    context = ""

    for doc in results:

        source = doc.metadata.get("source", "Unknown")
        source = str(source).replace("\\", "/").split("/")[-1]

        page = doc.metadata.get("page", "Unknown")

        if isinstance(page, int):
            page += 1

        context += f"""
Source: {source}
Page: {page}
Content: {doc.page_content}

"""

    return context


@tool
def analyze_business_data(analysis_type: str, n: int = 5) -> str:
    """Analyze sales data by region, category, or top products."""

    if analysis_type == "regional":
        return str(regional_analysis())

    elif analysis_type == "category":
        return str(category_analysis())

    elif analysis_type == "top_products":
        return str(top_products(n))

    return "Invalid analysis type."


# =====================================
# 7. PYDANTIC RESPONSE
# =====================================

class AgentResponse(BaseModel):
    answer: str
    sources: list[str]
    insights: list[str]


structured_llm = llm.with_structured_output(AgentResponse)


# =====================================
# 8. LANGGRAPH STATE
# =====================================

from typing import TypedDict, NotRequired
class AgentState(TypedDict):
    question: str
    route: str
    context: str
    answer: dict
    history: NotRequired[list]

# =====================================
# 9. ROUTER NODE
# =====================================

def router_node(state: AgentState):

    prompt = f"""
    Decide which capability is needed.

    Question: {state['question']}

    Reply with exactly one word:
    documents, analytics, or both.
    """

    response = llm.invoke(prompt)

    route = get_text(response).strip().lower().replace(".", "")

    if route not in ["documents", "analytics", "both"]:
        route = "both"

    return {"route": route}


# =====================================
# 10. ANALYSIS TYPE
# =====================================

def get_analysis_type(question):

    prompt = f"""
    Choose the correct analysis for this question.

    Question: {question}

    Return only one:
    regional, category, top_products
    """

    response = llm.invoke(prompt)

    analysis_type = get_text(response).strip().lower().replace(".", "")

    if analysis_type not in ["regional", "category", "top_products"]:
        return None

    return analysis_type


# =====================================
# 11. DOCUMENT NODE
# =====================================

def document_node(state: AgentState):

    try:
        result = search_documents.invoke({
            "question": state["question"]
        })

        return {"context": result}

    except Exception as e:
        return {"context": f"Document search failed: {e}"}


# =====================================
# 12. ANALYTICS NODE
# =====================================

def analytics_node(state: AgentState):

    try:
        analysis_type = get_analysis_type(state["question"])

        if not analysis_type:
            return {"context": "Could not identify the required analysis."}

        result = analyze_business_data.invoke({
            "analysis_type": analysis_type,
            "n": 5
        })

        return {
            "context": f"Source: sales_data.csv\n{result}"
        }

    except Exception as e:
        return {"context": f"Analytics failed: {e}"}


# =====================================
# 13. BOTH NODE
# =====================================

def both_node(state: AgentState):

    try:
        doc_result = search_documents.invoke({
            "question": state["question"]
        })

        analysis_type = get_analysis_type(state["question"])

        if not analysis_type:
            return {"context": f"DOCUMENTS:\n{doc_result}"}

        analytics_result = analyze_business_data.invoke({
            "analysis_type": analysis_type,
            "n": 5
        })

        return {
            "context": f"""
DOCUMENT INFORMATION:
{doc_result}

BUSINESS ANALYTICS:
Source: sales_data.csv
{analytics_result}
"""
        }

    except Exception as e:
        return {"context": f"Combined analysis failed: {e}"}


# =====================================
# 14. RESPONSE NODE
# =====================================

def response_node(state: AgentState):

    history = state.get("history", [])

    prompt = f"""
    You are an enterprise AI analytics assistant.

    Previous conversation:
    {history}

    Current question:
    {state['question']}

    Available information:
    {state['context']}

    Instructions:
    - Answer using available information.
    - Never invent facts or figures.
    - Include document filenames and page numbers in sources.
    - For analytics, mention sales_data.csv as the source.
    - Include relevant business findings in insights.
    - If information is unavailable, clearly say so.
    """

    response = structured_llm.invoke(prompt)

    answer = dict(response)

    history = history + [{
        "question": state["question"],
        "answer": answer["answer"]
    }]

    return {
        "answer": answer,
        "history": history
    }


# =====================================
# 15. SQLITE MEMORY
# =====================================

connection = sqlite3.connect(
    str(BASE_DIR / "enterprise_memory.db"),
    check_same_thread=False
)

checkpointer = SqliteSaver(connection)
checkpointer.setup()


# =====================================
# 16. BUILD WORKFLOW
# =====================================

builder = StateGraph(AgentState)

builder.add_node("router", router_node)
builder.add_node("documents", document_node)
builder.add_node("analytics", analytics_node)
builder.add_node("both", both_node)
builder.add_node("response", response_node)

builder.add_edge(START, "router")

builder.add_conditional_edges(
    "router",
    lambda state: state["route"],
    {
        "documents": "documents",
        "analytics": "analytics",
        "both": "both"
    }
)

builder.add_edge("documents", "response")
builder.add_edge("analytics", "response")
builder.add_edge("both", "response")

builder.add_edge("response", END)

workflow = builder.compile(
    checkpointer=checkpointer
)
