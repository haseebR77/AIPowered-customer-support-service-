# AI-Powered Customer Support Service

AI-powered chatbot service for FAQ handling and support request triage across multiple service domains.

## Overview

This project implements a full-stack customer support assistant using a pretrained NLP model and a FastAPI backend.  
The chatbot supports:

- FAQ answering
- Intent and domain classification
- Confidence scoring
- Escalation handling
- Interaction logging

The implementation is case-independent and uses a synthetic knowledge base to avoid dependency on any specific company dataset.

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI (Python)
- AI/NLP: `sentence-transformers/all-MiniLM-L6-v2` with lexical fallback
- Database: SQLite + SQLAlchemy
- Testing: PyTest

## Pretrained Model Used

This project uses the pretrained Sentence Transformer model:
`sentence-transformers/all-MiniLM-L6-v2`

## Architecture

`User -> React Frontend -> FastAPI Backend -> NLP Layer -> SQLite Database`

- `frontend/src/App.jsx`: chat UI and user interactions
- `frontend/src/api.js`: API client layer
- `backend/main.py`: API routes, orchestration, logging
- `backend/chatbot.py`: domain/intent detection + confidence + escalation logic
- `backend/faq_data.py`: synthetic domain intents and responses
- `backend/models.py`: request/response and DB models
- `backend/database.py`: database connection/session management

## Why This NLP Model

Model used: `sentence-transformers/all-MiniLM-L6-v2`

Why selected:
- Lightweight and fast for local inference
- Strong semantic similarity quality for FAQ-style intent matching
- Works well with short support queries

How matching works:
1. Keyword matching (fast path for known intent phrases)
2. Embedding similarity (semantic search over FAQ questions)
3. Lexical fallback if model is unavailable

Confidence logic:
- Keyword hit starts from high confidence
- Semantic/lexical similarity scores are normalized into confidence values

Escalation logic:
- Base threshold: `confidence < 0.50 -> escalated`
- Forced escalation for sensitive intents (e.g. urgent medical help, unknown transaction, blocked card)
- Unknown fallback for complex/unrecognized queries

## Supported Domains

### Ecommerce
- `order_status`, `refund_request`, `return_policy`, `delivery_info`, `payment_methods`

### Healthcare
- `appointment_booking`, `clinic_timings`, `online_consultation`, `cancel_appointment`, `urgent_medical_help`

### Banking
- `atm_pin_reset`, `card_blocked`, `unknown_transaction`, `account_opening`, `payment_failed`

## API Endpoints

### `POST /ask`
Classifies and responds to a user query, then logs the interaction.

Example response:
```json
{
  "query": "Where is my order?",
  "domain": "ecommerce",
  "intent": "order_status",
  "confidence": 0.83,
  "response": "You can track your order using your order ID in the order tracking section.",
  "escalated": false,
  "response_time_ms": 54.2
}
```

### `POST /escalate`
Manual escalation route.

```json
{
  "status": "success",
  "message": "Your query has been escalated to human support."
}
```

### `GET /logs`
Returns full interaction logs (latest first).

### `GET /log`
Alias route for `/logs`.

### `GET /health`
Service health check.

Swagger/OpenAPI docs: `http://127.0.0.1:8000/docs`

## Logging Schema

Each interaction stores:
- `user_query`
- `detected_domain`
- `detected_intent`
- `bot_response`
- `confidence`
- `escalated`
- `response_time_ms`
- `timestamp`

Database file: `backend/support_logs.db`

## Performance and Accuracy Notes

- Target response time: `< 2s`
- Lightweight query-result caching is enabled in chatbot inference path.
- Existing tests validate routing, intent behavior, escalation, and log integrity.
- Accuracy target is `> 80%` for synthetic domain test queries.

## Run Locally

From project root:

```bash
pip install -r backend/requirements.txt
```

Backend:
```bash
cd backend
uvicorn main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

URLs:
- Backend: `http://127.0.0.1:8000`
- Frontend: `http://localhost:5173`

## Testing

Run all tests:
```bash
pytest
```

Optional evaluation script:
```bash
python evaluate.py
```

## Clean Submission Notes

For final university submission zip, exclude generated/runtime folders:
- `frontend/node_modules`
- `.git`
- `__pycache__`
- `.pytest_cache`

These are already ignored by `.gitignore`.

## Future Enhancements

- LLM integration (OpenAI-compatible route)
- Multilingual intent support
- Voice chatbot interface
- Human-support dashboard with ticket lifecycle
- Authentication and role-based access
- Fine-tuned domain transformer model
