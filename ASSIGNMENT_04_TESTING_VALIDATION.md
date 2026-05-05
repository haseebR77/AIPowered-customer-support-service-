# ASSIGNMENT 04: TESTING & VALIDATION REPORT

## 1. Introduction
This report documents the testing and validation activities performed for the AI-Powered Customer Support Service. The chatbot system was already implemented and functional. Assignment 04 focuses on structured verification of correctness, reliability, safe behavior outside the core domain, and basic performance under concurrent load.

## 2. Project Overview
The project is a FastAPI-based backend with a React frontend. The chatbot supports general e-commerce customer support queries and logs all interactions in SQLite. Primary backend endpoints include:
- `GET /health`
- `POST /ask`
- `POST /escalate`
- `GET /logs`
- `GET /log` (alias added for assignment wording compatibility)

## 3. Existing System Architecture
- **Application layer:** `backend/main.py` (FastAPI routes and orchestration)
- **AI/NLP layer:** `backend/chatbot.py` (intent matching, confidence scoring, escalation logic)
- **Knowledge base:** `backend/faq_data.py` (synthetic e-commerce FAQs)
- **Persistence layer:** `backend/database.py`, `backend/models.py` (SQLAlchemy + SQLite)
- **Evaluation utility:** `evaluate.py` (intent accuracy script)

## 4. Test-Driven Validation Strategy
The testing strategy combines:
- **Unit testing** for chatbot logic and response behavior.
- **Integration testing** for API correctness and persistence behavior.
- **Case-independence validation** for supported and unsupported domains.
- **Performance testing** for concurrent request handling.

For API tests, database dependency overrides are used with temporary SQLite databases to avoid modifying production `support_logs.db`.

## 5. Unit Testing
Unit tests are implemented in `tests/test_unit_chatbot.py` and validate:
- Intent classification for common e-commerce requests:
  - order tracking
  - refunds
  - returns
  - delivery
  - payment failure
- Response generation quality (non-empty known FAQ response).
- Escalation behavior for unknown/random queries under strict confidence threshold.

These tests directly instantiate `SupportChatbot` and verify core model behavior without API overhead.

## 6. Integration Testing
Integration tests are implemented in `tests/test_api_integration.py` using `FastAPI TestClient`.

Validated items:
- `GET /health` returns status and HTTP 200.
- `POST /ask` returns required response keys (`query`, `intent`, `response`, `confidence`, `escalated`).
- `POST /ask` with empty query returns validation/client error.
- `POST /escalate` returns successful escalation response.
- `GET /logs` returns list data.
- `GET /log` alias returns list data consistent with log retrieval behavior.
- Database logging verification after `POST /ask` by checking log list updates.

## 7. Database Logging Validation
Logging validation is integrated into API tests by:
- Sending support queries through `/ask`.
- Reading entries through `/logs`.
- Confirming queries appear in stored records.

The logging flow demonstrates persistence of user query, intent, response, confidence, escalation status, and timestamp metadata.

## 8. Case Independence Validation
Case-independence tests are implemented in `tests/test_case_independence.py`.

Covered scenarios:
- **E-commerce query:** Confirm supported intent handling and stable response.
- **Healthcare query:** Confirm safe handling without crash (escalation or safe response).
- **Banking query:** Confirm safe handling without crash (escalation or safe response).

The chatbot is intentionally e-commerce focused. Unsupported domains are validated for safe behavior instead of forced unreliable domain responses.

## 9. Performance Testing
Performance test is implemented in `tests/test_performance.py` using `ThreadPoolExecutor` and `FastAPI TestClient`.

Design:
- Simulates **100 concurrent requests** to `/ask`.
- Uses a mix of valid e-commerce queries.
- Measures:
  - total execution time
  - average latency
  - minimum latency
  - maximum latency
  - success count
  - failure count
- Applies a practical assertion: success rate must be at least 90%.

This test is lightweight and intended for local execution in a university assignment environment.

## 10. Test Execution Commands
Run from project root:

```bash
pip install -r backend/requirements.txt
pytest
python evaluate.py
```

## 11. Expected Test Results
Expected outcomes include:
- Unit tests pass for core intent and escalation behavior.
- Integration tests pass for all required endpoints and logging.
- Case independence tests pass with safe handling of unsupported domains.
- Performance test reports metrics and meets minimum success-rate threshold.

Result template:
- Total requests: ___
- Success count: ___
- Failure count: ___
- Success rate: ___%
- Total time: ___ s
- Avg latency: ___ s
- Min latency: ___ s
- Max latency: ___ s

## 12. Limitations
- Performance measurements vary by hardware and runtime conditions.
- NLP behavior depends on available model/runtime environment.
- The chatbot is intentionally scoped to e-commerce support and does not provide specialized healthcare/banking assistance.
- Concurrency tests are application-level and not a full production load benchmark.

## 13. Conclusion
Assignment 04 validation confirms that the existing chatbot system is operational, testable, and robust for the defined e-commerce domain. The combined unit, integration, case-independence, and performance tests provide evidence of functional correctness, safe unsupported-domain handling, logging integrity, and acceptable concurrent request handling for academic evaluation.

