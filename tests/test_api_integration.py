import os
import tempfile

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.main import app, get_db


@pytest.fixture()
def client():
    temp_dir = tempfile.mkdtemp(prefix="chatbot_tests_")
    db_path = os.path.join(temp_dir, "test_support_logs.db")
    test_db_url = f"sqlite:///{db_path}"

    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    engine.dispose()


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"


def test_ask_endpoint_success(client: TestClient):
    response = client.post("/ask", json={"query": "Where is my order?"})
    assert response.status_code == 200
    payload = response.json()
    for key in ["query", "domain", "intent", "response", "confidence", "escalated", "response_time_ms"]:
        assert key in payload
    assert payload["domain"] == "ecommerce"
    assert payload["intent"] == "order_status"
    assert payload["response_time_ms"] >= 0


def test_ask_endpoint_empty_query_validation(client: TestClient):
    response = client.post("/ask", json={"query": ""})
    assert response.status_code in (400, 422)


def test_escalate_endpoint(client: TestClient):
    response = client.post(
        "/escalate",
        json={
            "query": "This issue requires human help",
            "reason": "Manual test escalation",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "success"
    assert "escalated" in payload["message"].lower()


def test_logs_and_log_alias(client: TestClient):
    client.post("/ask", json={"query": "How can I return my product?"})

    logs_response = client.get("/logs")
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert isinstance(logs_payload, list)
    assert logs_payload
    first_log = logs_payload[0]
    for key in [
        "user_query",
        "detected_domain",
        "detected_intent",
        "confidence",
        "bot_response",
        "escalated",
        "response_time_ms",
        "timestamp",
    ]:
        assert key in first_log

    log_alias_response = client.get("/log")
    assert log_alias_response.status_code == 200
    log_alias_payload = log_alias_response.json()
    assert isinstance(log_alias_payload, list)


def test_logs_capture_query_after_ask(client: TestClient):
    query = "I want a refund."
    before_count = len(client.get("/logs").json())

    ask_response = client.post("/ask", json={"query": query})
    assert ask_response.status_code == 200

    after_logs = client.get("/logs").json()
    assert len(after_logs) >= before_count + 1
    assert any(item["user_query"] == query for item in after_logs)


def test_healthcare_and_banking_ask_endpoint(client: TestClient):
    healthcare = client.post("/ask", json={"query": "What are your clinic timings?"})
    assert healthcare.status_code == 200
    healthcare_payload = healthcare.json()
    assert healthcare_payload["domain"] == "healthcare"
    assert healthcare_payload["intent"] == "clinic_timings"
    assert healthcare_payload["escalated"] is False

    banking = client.post("/ask", json={"query": "I found an unknown transaction."})
    assert banking.status_code == 200
    banking_payload = banking.json()
    assert banking_payload["domain"] == "banking"
    assert banking_payload["intent"] == "unknown_transaction"
    assert banking_payload["escalated"] is True


def test_required_domain_examples(client: TestClient):
    cases = [
        ("Where is my order?", "ecommerce", "order_status", False),
        ("I want a refund.", "ecommerce", "refund_request", False),
        ("How can I return my product?", "ecommerce", "return_policy", False),
        ("How can I book a doctor appointment?", "healthcare", "appointment_booking", False),
        ("What are your clinic timings?", "healthcare", "clinic_timings", False),
        ("I need urgent medical help.", "healthcare", "urgent_medical_help", True),
        ("How can I reset my ATM PIN?", "banking", "atm_pin_reset", False),
        ("My card is blocked.", "banking", "card_blocked", True),
        ("I found an unknown transaction.", "banking", "unknown_transaction", True),
    ]
    for query, domain, intent, escalated in cases:
        response = client.post("/ask", json={"query": query})
        assert response.status_code == 200
        payload = response.json()
        assert payload["domain"] == domain
        assert payload["intent"] == intent
        assert payload["escalated"] is escalated


def test_ask_rejects_whitespace_query(client: TestClient):
    response = client.post("/ask", json={"query": "   "})
    assert response.status_code in (400, 422)

