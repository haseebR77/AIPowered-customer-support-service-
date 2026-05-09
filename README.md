# AI-Powered Customer Support Service

This is a full-stack customer support chatbot built with React + FastAPI.
It supports three domains:

- Ecommerce
- Healthcare
- Banking

For each query, the bot detects domain and intent, generates a response, assigns confidence, decides escalation, and stores the interaction in SQLite logs.

## Key Features

- Domain detection (`ecommerce`, `healthcare`, `banking`, `general`)
- Intent detection for each domain
- Confidence-based and safety-based escalation
- Manual escalation endpoint
- Persistent logs with domain, intent, response, and timestamp
- Frontend chat UI with interaction logs

## Tech Stack

- Frontend: React + Vite
- Backend: FastAPI (Python)
- NLP approach: Sentence embeddings with lexical/keyword fallback
- Database: SQLite + SQLAlchemy
- Testing: PyTest

## Run Locally

From project root:

```bash
pip install -r backend/requirements.txt
```

Start backend (Terminal 1):

```bash
cd backend
uvicorn main:app --reload
```

Backend: `http://127.0.0.1:8000`

Start frontend (Terminal 2):

```bash
cd frontend
npm install
npm run dev
```

Frontend: `http://localhost:5173`

## API

### `POST /ask`

Returns:

```json
{
  "query": "Where is my order?",
  "domain": "ecommerce",
  "intent": "order_status",
  "confidence": 0.92,
  "response": "You can track your order using your order ID in the order tracking section.",
  "escalated": false
}
```

### `POST /escalate`

Manual escalation response:

```json
{
  "status": "success",
  "message": "Your query has been escalated to human support."
}
```

### Other routes
- `GET /logs` and `GET /log`: returns logs (latest first)
- `GET /health`: service health check

## Supported Domains and Intents

### Ecommerce

- `order_status`
- `refund_request`
- `return_policy`
- `delivery_info`
- `payment_methods`

### Healthcare

- `appointment_booking`
- `clinic_timings`
- `online_consultation`
- `cancel_appointment`
- `urgent_medical_help`

### Banking

- `atm_pin_reset`
- `card_blocked`
- `unknown_transaction`
- `account_opening`
- `payment_failed`

## Escalation Rules

- Threshold:
  - `confidence < 0.50` => escalated
  - `confidence >= 0.50` => not escalated

- Forced escalation also applies to sensitive cases:
  - urgent medical help
  - unknown transaction
  - blocked card
  - payment failed with deducted amount context
  - explicit request for human support
  - unknown/complex queries

Unknown fallback example:

```json
{
  "query": "My problem is very complicated and not listed here.",
  "domain": "general",
  "intent": "unknown",
  "confidence": 0.49,
  "response": "I am not fully sure about this issue, so I will escalate it to human support.",
  "escalated": true
}
```

## Log Fields

Each log entry stores:

```json
{
  "user_query": "Where is my order?",
  "detected_domain": "ecommerce",
  "detected_intent": "order_status",
  "confidence": 0.92,
  "bot_response": "You can track your order using your order ID in the order tracking section.",
  "escalated": false,
  "timestamp": "2026-05-09 14:30:00"
}
```

## Run Tests

```bash
pytest
```

Optional:
```bash
python evaluate.py
```

## Quick Demo Queries

- Ecommerce: `Where is my order?`, `I want a refund.`
- Healthcare: `How can I book a doctor appointment?`, `I need urgent medical help.`
- Banking: `How can I reset my ATM PIN?`, `I found an unknown transaction.`
