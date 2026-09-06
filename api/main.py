import uuid
import sys
import os

# Project root ko path me add karo
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agent.multi_graph_builder import multi_agent_graph
from database.save_step import save_step
from database.save_session import save_session
from database.create_tables import create_tables
from memory.session_memory import add_session_memory

create_tables()

app = FastAPI(title="AI Agent API")

# React ke liye CORS allow karo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────
# REQUEST / RESPONSE MODELS
# ─────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "AI Agent API is running 🤖"}


@app.post("/chat")
def chat(request: ChatRequest):

    session_id = uuid.uuid4()

    # Step 1 — User Input save karo
    save_step(session_id, 1, "User Input", request.query)
    add_session_memory(f"User: {request.query}")

    # LangGraph invoke karo
    result = multi_agent_graph.invoke(
        {
            "query":              request.query,
            "session_id":         str(session_id),
            "memory":             "",
            "task_queue":         [],
            "current_task":       "",
            "research_result":    "",
            "calculation_result": "",
            "weather_result":     "",
            "database_result":    "",
            "file_result":        "",
            "email_result":       "",
            "final_answer":       ""
        },
        {"recursion_limit": 25}
    )

    final_answer = result["final_answer"]

    # Session save karo
    save_session(session_id, request.query, final_answer)

    # PDF ya DB file check karo
    has_pdf     = "output.pdf"              in final_answer
    has_db_file = "[DOWNLOAD_FILE:db_result.txt]" in final_answer

    # Download signals answer se hato
    clean_answer = final_answer.replace("[DOWNLOAD_FILE:db_result.txt]", "").strip()

    return {
        "answer":     clean_answer,
        "session_id": str(session_id),
        "has_pdf":    has_pdf,
        "has_db_file": has_db_file
    }


@app.get("/download/pdf")
def download_pdf():
    return FileResponse(
        "output.pdf",
        filename="result.pdf",
        media_type="application/pdf"
    )


@app.get("/download/db")
def download_db():
    return FileResponse(
        "db_result.txt",
        filename="db_result.txt",
        media_type="text/plain"
    )
