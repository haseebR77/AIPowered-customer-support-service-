# AI-Powered Customer Support Service

## Project Overview
This project is a complete full-stack customer support chatbot for e-commerce FAQs and service requests. It uses a pretrained NLP sentence-embedding model to match customer questions with synthetic FAQ answers, escalates low-confidence queries to human support, and logs every interaction in SQLite.

## Features
- Answers common customer support FAQs.
- Handles service topics: order status, refunds, returns, delivery, payment issues, availability, and more.
- Confidence-based escalation to human support.
- Manual escalation endpoint and UI trigger.
- Full interaction logging in SQLite.
- React chat UI with confidence and escalation badges.
- Logs viewer in the frontend.
- Evaluation script for intent accuracy.

## Tech Stack
- Frontend: React + Vite
- Backend: FastAPI (Python)
- NLP: `sentence-transformers/all-MiniLM-L6-v2` (with lexical fallback)
- Database: SQLite + SQLAlchemy

## Folder Structure
```text
PFAI_Assignment_03/
+-- backend/
¦   +-- __init__.py
¦   +-- main.py
¦   +-- database.py
¦   +-- models.py
¦   +-- chatbot.py
¦   +-- faq_data.py
¦   +-- requirements.txt
+-- frontend/
¦   +-- package.json
¦   +-- vite.config.js
¦   +-- index.html
¦   +-- src/
¦       +-- App.jsx
¦       +-- main.jsx
¦       +-- api.js
¦       +-- styles.css
+-- evaluate.py
+-- README.md
```

## How to Run Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at `http://127.0.0.1:8000`.

## How to Run Frontend
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at `http://127.0.0.1:5173`.

## API Endpoints
### `POST /ask`
- Accepts a user query.
- Detects best FAQ intent.
- Returns answer, confidence, escalation status.
- Logs interaction to SQLite.

Example response:
```json
{
  "query": "How can I return my product?",
  "intent": "return_policy",
  "response": "You can return eligible products within 7 days of delivery...",
  "confidence": 0.91,
  "escalated": false
}
```

Low-confidence example:
```json
{
  "query": "My problem is complicated",
  "intent": "unknown",
  "response": "I could not confidently answer your query. Your request has been escalated to a human support agent.",
  "confidence": 0.42,
  "escalated": true
}
```

### `POST /escalate`
- Manually escalates a query to a human agent.
- Stores escalation record in logs.

### `GET /logs`
- Returns all interaction logs in reverse chronological order.

### `GET /health`
- Health check endpoint.

## Example Queries
- "Where is my order?"
- "How do I return a product?"
- "Why did my payment fail?"
- "Can I cancel my order?"
- "How can I download my invoice?"

## Escalation Logic
- Chatbot computes a confidence score from semantic similarity.
- If confidence is below threshold (`0.62`), it escalates automatically.
- Users can also manually escalate through `POST /escalate` or the frontend button.

## Log Storage
Logs are stored in SQLite (`backend/support_logs.db`) with:
- `id`
- `user_query`
- `detected_intent`
- `bot_response`
- `confidence`
- `escalated`
- `timestamp`

## Testing and Accuracy Evaluation
Run:
```bash
python evaluate.py
```
The script prints:
- Total test queries
- Correct predictions
- Accuracy percentage

Target for assignment: **Above 80%**.

## Plan-Driven Design Explanation
### 1. Requirement Analysis
Functional requirements implemented:
- FAQ answering
- Service request handling for key support intents
- Low-confidence escalation
- Logging every interaction in database

Non-functional requirements addressed:
- Fast FAQ lookup via precomputed embeddings (target <2s)
- Evaluation script for >80% accuracy check
- Modular backend/frontend folder design
- Case-independent query matching through normalized similarity

### 2. System Design
Architecture:
- React frontend chat interface with logs viewer
- FastAPI backend exposing `/ask`, `/escalate`, `/logs`, `/health`
- AI layer using pretrained sentence-transformer similarity
- SQLite persistence via SQLAlchemy models

### 3. Implementation Plan
Executed in modules:
- `faq_data.py` for synthetic FAQ knowledge base
- `chatbot.py` for intent matching and confidence scoring
- `database.py` + `models.py` for schema/session management
- `main.py` for API orchestration and CORS
- React UI (`App.jsx`, `api.js`, `styles.css`) for user interaction
- `evaluate.py` for measurable testing

### 4. Case Independence
- FAQ data is synthetic and general e-commerce support data.
- No private company data is required.
- Intents and responses are reusable across multiple e-commerce businesses.

### 5. Testing and Evaluation
- `evaluate.py` runs 12 sample queries across multiple intents.
- Accuracy is calculated as `correct / total`.
- Confirms assignment target performance and validates chatbot behavior.

## How This Satisfies Assignment Requirements
- Full stack implementation completed.
- Required endpoint set implemented.
- Required FAQ categories included (15+ intents).
- Confidence + escalation behavior implemented.
- SQLite logging implemented and visible via API/UI.
- Accuracy evaluation script included.
- Modular, readable, and locally runnable codebase.
