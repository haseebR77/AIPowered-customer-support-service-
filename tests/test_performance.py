import os
import random
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.database import Base
from backend.main import app, get_db


@pytest.fixture()
def performance_client():
    temp_dir = tempfile.mkdtemp(prefix="chatbot_perf_tests_")
    db_path = os.path.join(temp_dir, "perf_support_logs.db")
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
    yield
    app.dependency_overrides.clear()
    engine.dispose()


def test_100_concurrent_requests(performance_client):
    queries = [
        "Where is my order?",
        "How can I return my product?",
        "Why did my payment fail?",
        "How long does delivery take?",
        "How can I download my invoice?",
    ]

    latencies = []
    success_count = 0
    failure_count = 0
    total_requests = 100

    def send_request():
        query = random.choice(queries)
        start = time.perf_counter()
        with TestClient(app) as client:
            response = client.post("/ask", json={"query": query})
        duration = time.perf_counter() - start
        return response.status_code, duration

    start_total = time.perf_counter()
    with ThreadPoolExecutor(max_workers=20) as executor:
        futures = [executor.submit(send_request) for _ in range(total_requests)]
        for future in as_completed(futures):
            status_code, latency = future.result()
            latencies.append(latency)
            if status_code == 200:
                success_count += 1
            else:
                failure_count += 1

    total_time = time.perf_counter() - start_total
    avg_latency = sum(latencies) / len(latencies)
    min_latency = min(latencies)
    max_latency = max(latencies)
    success_rate = (success_count / total_requests) * 100

    print("\nPerformance Test Results")
    print(f"Total requests: {total_requests}")
    print(f"Success count: {success_count}")
    print(f"Failure count: {failure_count}")
    print(f"Success rate: {success_rate:.2f}%")
    print(f"Total time: {total_time:.4f} seconds")
    print(f"Average latency: {avg_latency:.4f} seconds")
    print(f"Min latency: {min_latency:.4f} seconds")
    print(f"Max latency: {max_latency:.4f} seconds")

    assert success_rate >= 90

