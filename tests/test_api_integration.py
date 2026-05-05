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
    for key in ["query", "intent", "response", "confidence", "escalated"]:
        assert key in payload


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
    assert payload["escalated"] is True


def test_logs_and_log_alias(client: TestClient):
    client.post("/ask", json={"query": "How can I return a product?"})

    logs_response = client.get("/logs")
    assert logs_response.status_code == 200
    logs_payload = logs_response.json()
    assert isinstance(logs_payload, list)

    log_alias_response = client.get("/log")
    assert log_alias_response.status_code == 200
    log_alias_payload = log_alias_response.json()
    assert isinstance(log_alias_payload, list)


def test_logs_capture_query_after_ask(client: TestClient):
    query = "What are shipping charges?"
    before_count = len(client.get("/logs").json())

    ask_response = client.post("/ask", json={"query": query})
    assert ask_response.status_code == 200

    after_logs = client.get("/logs").json()
    assert len(after_logs) >= before_count + 1
    assert any(item["user_query"] == query for item in after_logs)

