
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_core.runnables import RunnableConfig

from agent.workflow import workflow


app = FastAPI(
    title="Enterprise AI Knowledge & Analytics Agent",
    description="AI-powered document search and business analytics",
    version="1.0"
)



from pydantic import BaseModel, Field, field_validator


class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    thread_id: str = "default"

    @field_validator("question")
    @classmethod
    def validate_question(cls, value):
        if not value.strip():
            raise ValueError("Question cannot be empty")
        return value



@app.get("/health")
def health_check():
    return {
        "status": "running",
        "message": "AI Agent API is working"
    }


@app.post("/ask")
def ask_question(request: QuestionRequest):

    config: RunnableConfig = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }

    try:

        result = workflow.invoke(
            {
                "question": request.question,
                "route": "",
                "context": "",
                "answer": {}
            },
            config=config
        )

        return result["answer"]

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
