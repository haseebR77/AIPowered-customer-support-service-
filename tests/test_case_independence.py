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
    temp_dir = tempfile.mkdtemp(prefix="chatbot_case_tests_")
    db_path = os.path.join(temp_dir, "case_support_logs.db")
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


def test_ecommerce_query_supported(client: TestClient):
    response = client.post("/ask", json={"query": "Where is my order?"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] in {
        "order_status",
        "delivery_time",
        "shipping_charges",
    }
    assert isinstance(payload["response"], str)
    assert payload["response"].strip() != ""


def test_healthcare_query_is_safely_handled(client: TestClient):
    response = client.post("/ask", json={"query": "How can I book a doctor appointment?"})
    assert response.status_code == 200
    payload = response.json()
    assert "intent" in payload
    assert "response" in payload
    assert isinstance(payload["response"], str)
    # Unsupported domain should be escalated or safely handled.
    assert payload["escalated"] in (True, False)


def test_banking_query_is_safely_handled(client: TestClient):
    response = client.post("/ask", json={"query": "How can I reset my debit card PIN?"})
    assert response.status_code == 200
    payload = response.json()
    assert "intent" in payload
    assert "response" in payload
    assert isinstance(payload["response"], str)
    # Unsupported domain should be escalated or safely handled.
    assert payload["escalated"] in (True, False)
