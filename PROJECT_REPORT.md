# AI-Powered Customer Support Service
## Academic Project Report

### Title Page
- **Project Title:** AI-Powered Customer Support Service
- **Course:** Artificial Intelligence / Software Engineering Lab
- **Student:** [Your Name]
- **Submission Date:** [Date]

## 1. Introduction
This project implements an AI-powered customer support chatbot that handles FAQs and service requests through a web interface and REST APIs. The system combines a pretrained NLP model with rule-based safety controls to generate responses, assign confidence, escalate unresolved issues, and log all interactions.

## 2. Objectives
- Build a modular full-stack chatbot application.
- Use a pretrained NLP model for intent understanding.
- Support reliable escalation for unresolved/sensitive requests.
- Maintain persistent interaction logs for analysis.
- Validate the system through unit, API, and performance tests.

## 3. Functional Requirements
- FAQ answering across supported domains.
- Escalation for unresolved or sensitive queries.
- Logging of each interaction with confidence and metadata.
- API endpoints:
  - `POST /ask`
  - `POST /escalate`
  - `GET /logs` (and alias `GET /log`)

## 4. Non-Functional Requirements
- Average response time target below 2 seconds for local test scenarios.
- Target intent accuracy above 80% on synthetic benchmark queries.
- Clean modular architecture and readable code.

## 5. System Architecture
`User -> React Frontend -> FastAPI Backend -> NLP Layer -> SQLite Database`

- **Frontend (React + Vite):** chat interface, loading/error states, logs panel.
- **Backend (FastAPI):** route orchestration, validation, persistence.
- **AI Layer:** pretrained sentence-transformer with lexical fallback.
- **Database:** SQLite with SQLAlchemy ORM for interaction logs.

## 6. Technologies Used
- React + Vite
- FastAPI
- SQLAlchemy + SQLite
- Sentence Transformers (`all-MiniLM-L6-v2`)
- PyTest

## 7. Implementation Details

### 7.1 NLP and Intent Matching
- Primary semantic model: `sentence-transformers/all-MiniLM-L6-v2`.
- Fallback strategy:
  1. Keyword match (fast, deterministic)
  2. Embedding similarity
  3. Lexical similarity fallback

### 7.2 Confidence and Escalation
- Base threshold: `confidence < 0.50 => escalation`.
- Forced escalation for high-risk cases (e.g., urgent medical help, unknown transaction, blocked card, explicit human support requests).
- Unknown query fallback returns safe escalation response.

### 7.3 Logging Design
Each query is stored with:
- `user_query`
- `detected_domain`
- `detected_intent`
- `bot_response`
- `confidence`
- `escalated`
- `response_time_ms`
- `timestamp`

## 8. Database Design
- Database: `backend/support_logs.db`
- Main table: `interaction_logs`
- Stores both automatic chatbot responses and manual escalation events.

## 9. API Endpoints

### `POST /ask`
- Validates input query
- Generates response and confidence
- Applies escalation rules
- Persists interaction

### `POST /escalate`
- Manually escalates user request
- Logs escalation event

### `GET /logs` and `GET /log`
- Returns chronological log history (latest first)

### `GET /health`
- Returns service status and timestamp

## 10. Testing and Results

### Test Coverage
- Unit tests for chatbot classification and escalation behavior.
- API integration tests for endpoint correctness and logging.
- Case-independence tests for ecommerce, healthcare, and banking.
- Performance test for concurrent request handling.

### Observations
- Required routes are functional.
- Logs persist with expected metadata fields.
- Escalation behavior follows threshold and safety logic.
- Local test suite passes with target behavior.

## 11. Challenges Faced
- Balancing confidence thresholds vs over-escalation.
- Handling unknown queries safely without misleading responses.
- Preserving backward compatibility while extending schema fields.
- Keeping frontend responsive during async operations.

## 12. Future Enhancements
- LLM-based response generation for broader query coverage.
- Voice-enabled chatbot interface.
- Multi-language support.
- Human support dashboard and ticket assignment workflow.
- User authentication and role-based access.
- Fine-tuned domain-specific transformer model.

## 13. Conclusion
The project successfully delivers an AI-powered customer support service with modular architecture, pretrained NLP integration, robust escalation handling, and persistent logging. It satisfies assignment goals for functionality, system design, case independence, and validation through testing.

## 14. Suggested Screenshots for Submission
- Frontend chat interface with sample interaction.
- Swagger docs page (`/docs`) showing all endpoints.
- Terminal output for successful test run (`pytest`).
- SQLite log records from `support_logs.db`.
- Architecture diagram slide with data flow.

## 15. Final Submission Checklist
- [ ] Backend and frontend run successfully
- [ ] API docs accessible at `/docs`
- [ ] Logs generated in SQLite
- [ ] Tests executed and passing
- [ ] README updated
- [ ] Report attached
- [ ] Runtime/cache folders excluded from zip (`node_modules`, `.git`, `__pycache__`, `.pytest_cache`)
