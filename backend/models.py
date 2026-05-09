from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String

try:
    from .database import Base
except ImportError:  # pragma: no cover
    from database import Base


class InteractionLog(Base):
    __tablename__ = "interaction_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_query = Column(String, nullable=False)
    detected_domain = Column(String, nullable=False, default="general")
    detected_intent = Column(String, nullable=False, default="unknown")
    bot_response = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    escalated = Column(Boolean, nullable=False, default=False)
    response_time_ms = Column(Float, nullable=False, default=0.0)
    timestamp = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))


class AskRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Customer question to classify and answer.",
        examples=["Where is my order?"],
    )


class EscalateRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Original customer query that should be escalated.",
        examples=["My issue is complex and I need human help."],
    )
    reason: str = Field(
        default="Manual escalation requested by user.",
        max_length=1000,
        description="Optional reason explaining why escalation is requested.",
        examples=["Customer explicitly requested a human support agent."],
    )


class AskResponse(BaseModel):
    query: str
    domain: str
    intent: str
    response: str
    confidence: float
    escalated: bool
    response_time_ms: float = Field(description="Time taken to generate response in milliseconds.")


class LogOut(BaseModel):
    id: int
    user_query: str
    detected_domain: str
    detected_intent: str
    bot_response: str
    confidence: float
    escalated: bool
    response_time_ms: float
    timestamp: datetime

    model_config = ConfigDict(from_attributes=True)


class EscalateResponse(BaseModel):
    status: str
    message: str
