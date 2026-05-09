from datetime import datetime, timezone
from time import perf_counter
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from sqlalchemy.orm import Session

try:
    from .chatbot import SupportChatbot
    from .database import Base, engine, get_db
    from .models import (
        AskRequest,
        AskResponse,
        EscalateRequest,
        EscalateResponse,
        InteractionLog,
        LogOut,
    )
except ImportError:  # pragma: no cover
    from chatbot import SupportChatbot
    from database import Base, engine, get_db
    from models import AskRequest, AskResponse, EscalateRequest, EscalateResponse, InteractionLog, LogOut


app = FastAPI(
    title="AI-Powered Customer Support Service",
    version="1.1.0",
    description=(
        "AI-powered support chatbot with multi-domain intent detection, "
        "confidence scoring, escalation handling, and interaction logging."
    ),
)
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
        if "response_time_ms" not in column_names:
            conn.execute(
                text(
                    "ALTER TABLE interaction_logs "
                    "ADD COLUMN response_time_ms FLOAT NOT NULL DEFAULT 0.0"
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


@app.exception_handler(SQLAlchemyError)
def handle_db_errors(_: Request, exc: SQLAlchemyError):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Database error occurred: {str(exc)}"},
    )


@app.exception_handler(Exception)
def handle_unexpected_errors(_: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Unexpected server error: {str(exc)}"},
    )


@app.get("/health", summary="Health check", tags=["System"])
def health_check() -> dict:
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post(
    "/ask",
    response_model=AskResponse,
    summary="Ask chatbot question",
    description=(
        "Classifies the query into domain and intent, generates a response, computes confidence, "
        "applies escalation rules, and logs the interaction."
    ),
    tags=["Chatbot"],
)
def ask_question(payload: AskRequest, db: Session = Depends(get_db)):
    started = perf_counter()
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        result = chatbot.ask(query)
    except Exception as exc:  # pragma: no cover - runtime safety
        raise HTTPException(status_code=500, detail=f"Failed to process query: {exc}") from exc

    response_time_ms = round((perf_counter() - started) * 1000, 2)
    result["response_time_ms"] = response_time_ms

    try:
        log = InteractionLog(
            user_query=query,
            detected_domain=result["domain"],
            detected_intent=result["intent"],
            bot_response=result["response"],
            confidence=result["confidence"],
            escalated=result["escalated"],
            response_time_ms=response_time_ms,
        )
        db.add(log)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise

    return result


@app.post(
    "/escalate",
    response_model=EscalateResponse,
    summary="Manually escalate customer query",
    description="Stores a manual escalation event in logs and returns a success message.",
    tags=["Chatbot"],
)
def escalate_query(payload: EscalateRequest, db: Session = Depends(get_db)):
    started = perf_counter()
    query = payload.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    response_message = (
        "Your request has been escalated to a human support agent. "
        f"Reason noted: {payload.reason}"
    )

    try:
        log = InteractionLog(
            user_query=query,
            detected_domain="general",
            detected_intent="manual_escalation",
            bot_response=response_message,
            confidence=0.0,
            escalated=True,
            response_time_ms=round((perf_counter() - started) * 1000, 2),
        )
        db.add(log)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
    return {"status": "success", "message": "Your query has been escalated to human support."}


@app.get(
    "/logs",
    response_model=List[LogOut],
    summary="Get interaction logs",
    description="Returns chatbot interaction logs in reverse chronological order.",
    tags=["Logs"],
)
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(InteractionLog).order_by(InteractionLog.id.desc()).all()
    return logs


@app.get(
    "/log",
    response_model=List[LogOut],
    summary="Get interaction logs (alias)",
    tags=["Logs"],
)
def get_log_alias(db: Session = Depends(get_db)):
    return get_logs(db)
