from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from .chatbot import SupportChatbot
    from .database import Base, engine, get_db
    from .models import AskRequest, AskResponse, EscalateRequest, InteractionLog, LogOut
except ImportError:  # pragma: no cover
    from chatbot import SupportChatbot
    from database import Base, engine, get_db
    from models import AskRequest, AskResponse, EscalateRequest, InteractionLog, LogOut


app = FastAPI(title="AI-Powered Customer Support Service", version="1.0.0")
Base.metadata.create_all(bind=engine)


def ensure_log_schema_columns() -> None:
    """Backfills newer log columns for existing SQLite databases."""
    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(interaction_logs)")).fetchall()
        column_names = {row[1] for row in rows}
        if "detected_domain" not in column_names:
            conn.execute(
                text(
                    "ALTER TABLE interaction_logs "
                    "ADD COLUMN detected_domain VARCHAR NOT NULL DEFAULT 'general'"
                )
            )


ensure_log_schema_columns()
chatbot = SupportChatbot(threshold=0.50)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@app.post("/ask", response_model=AskResponse)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = chatbot.ask(query)

    log = InteractionLog(
        user_query=query,
        detected_domain=result["domain"],
        detected_intent=result["intent"],
        bot_response=result["response"],
        confidence=result["confidence"],
        escalated=result["escalated"],
    )
    db.add(log)
    db.commit()

    return result


@app.post("/escalate")
def escalate_query(payload: EscalateRequest, db: Session = Depends(get_db)):
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    response_message = (
        "Your request has been escalated to a human support agent. "
        f"Reason noted: {payload.reason}"
    )

    log = InteractionLog(
        user_query=query,
        detected_domain="general",
        detected_intent="manual_escalation",
        bot_response=response_message,
        confidence=0.0,
        escalated=True,
    )

    db.add(log)
    db.commit()
    return {"status": "success", "message": "Your query has been escalated to human support."}


@app.get("/logs", response_model=List[LogOut])
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(InteractionLog).order_by(InteractionLog.id.desc()).all()
    return logs


@app.get("/log", response_model=List[LogOut])
def get_log_alias(db: Session = Depends(get_db)):
    return get_logs(db)
