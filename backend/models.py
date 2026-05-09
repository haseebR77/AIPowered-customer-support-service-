from datetime import datetime

from pydantic import BaseModel, Field
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
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)


class AskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)


class EscalateRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=1000)
    reason: str = Field(default="Manual escalation requested by user.", max_length=1000)


class AskResponse(BaseModel):
    query: str
    domain: str
    intent: str
    response: str
    confidence: float
    escalated: bool


class LogOut(BaseModel):
    id: int
    user_query: str
    detected_domain: str
    detected_intent: str
    bot_response: str
    confidence: float
    escalated: bool
    timestamp: datetime

    class Config:
        from_attributes = True
