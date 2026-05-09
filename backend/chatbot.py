from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Dict, List, Tuple

import numpy as np

try:
    from .faq_data import FAQ_ENTRIES
except ImportError:  # pragma: no cover - allows running from backend directory
    from faq_data import FAQ_ENTRIES


@dataclass
class MatchResult:
    domain: str
    intent: str
    answer: str
    confidence: float
    escalated: bool


class SupportChatbot:
    """FAQ matching chatbot using sentence embeddings with robust lexical fallbacks."""

    def __init__(self, threshold: float = 0.50) -> None:
        self.threshold = threshold
        self.faq_entries = FAQ_ENTRIES
        self.questions: List[str] = [entry["question"] for entry in self.faq_entries]
        self.intent_to_faq = {
            entry["intent"]: entry for entry in self.faq_entries
        }

        self._embedding_model = None
        self._faq_embeddings = None
        self._load_embedding_model()

        self.keyword_map: Dict[str, List[str]] = {
            "order_status": [
                "track",
                "tracking",
                "where is my order",
                "order status",
                "order update",
            ],
            "refund_request": ["refund", "money back", "refund request", "refund status"],
            "return_policy": ["return", "send back", "return policy", "return item"],
            "delivery_info": ["delivery", "arrive", "shipping time", "how long", "days"],
            "payment_methods": ["payment method", "payment options", "cards accepted", "wallet"],
            "appointment_booking": ["book appointment", "doctor appointment", "appointment booking"],
            "clinic_timings": ["clinic timing", "clinic hours", "open clinic", "visiting hours"],
            "online_consultation": ["online consultation", "video consultation", "telemedicine"],
            "cancel_appointment": ["cancel appointment", "reschedule appointment"],
            "urgent_medical_help": ["urgent medical help", "emergency", "severe pain", "ambulance"],
            "atm_pin_reset": ["atm pin", "reset pin", "debit pin", "card pin"],
            "card_blocked": ["card blocked", "blocked card", "card locked"],
            "unknown_transaction": ["unknown transaction", "unauthorized transaction", "fraud transaction"],
            "account_opening": ["open account", "new bank account", "account opening"],
            "payment_failed": ["payment failed", "transaction failed", "amount deducted", "deducted but failed"],
        }
        self._forced_escalation_intents = {
            "urgent_medical_help",
            "unknown_transaction",
            "card_blocked",
            "payment_failed",
        }
        self._human_support_keywords = [
            "human support",
            "human agent",
            "talk to agent",
            "customer support",
            "representative",
        ]

    def _load_embedding_model(self) -> None:
        """Loads a lightweight pretrained model when available."""
        try:
            from sentence_transformers import SentenceTransformer

            self._embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self._faq_embeddings = self._embedding_model.encode(self.questions, normalize_embeddings=True)
        except Exception:
            # Fallback keeps the app runnable even when model download is unavailable.
            self._embedding_model = None
            self._faq_embeddings = None

    @staticmethod
    def _lexical_similarity(q1: str, q2: str) -> float:
        q1_lower = q1.lower().strip()
        q2_lower = q2.lower().strip()

        ratio_score = SequenceMatcher(None, q1_lower, q2_lower).ratio()

        tokens_1 = set(q1_lower.split())
        tokens_2 = set(q2_lower.split())
        if not tokens_1 or not tokens_2:
            token_score = 0.0
        else:
            token_score = len(tokens_1 & tokens_2) / len(tokens_1 | tokens_2)

        return 0.65 * ratio_score + 0.35 * token_score

    def _embedding_similarity(self, query: str) -> np.ndarray | None:
        if self._embedding_model is None or self._faq_embeddings is None:
            return None

        query_embedding = self._embedding_model.encode([query], normalize_embeddings=True)
        return np.dot(self._faq_embeddings, query_embedding[0])

    def _keyword_match(self, query: str) -> Tuple[str, float] | None:
        query_lower = query.lower()
        best_intent = None
        best_score = 0

        for intent, keywords in self.keyword_map.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > best_score:
                best_score = score
                best_intent = intent

        if best_intent and best_score > 0:
            confidence = min(0.75 + (0.08 * best_score), 0.95)
            return best_intent, confidence

        return None

    def _should_force_escalation(self, query: str, intent: str) -> bool:
        query_lower = query.lower()
        if intent in self._forced_escalation_intents:
            return True
        if any(keyword in query_lower for keyword in self._human_support_keywords):
            return True
        if "payment" in query_lower and "deducted" in query_lower:
            return True
        return False

    def _find_best_faq(self, query: str) -> MatchResult:
        keyword_result = self._keyword_match(query)
        if keyword_result:
            intent, confidence = keyword_result
            selected_faq = self.intent_to_faq[intent]
            force_escalation = self._should_force_escalation(query, intent)
            return MatchResult(
                domain=selected_faq["domain"],
                intent=intent,
                answer=selected_faq["answer"],
                confidence=round(confidence, 2),
                escalated=force_escalation or round(confidence, 2) < self.threshold,
            )

        embed_scores = self._embedding_similarity(query)

        if embed_scores is not None:
            best_index = int(np.argmax(embed_scores))
            best_score = float(embed_scores[best_index])
        else:
            lexical_scores = [self._lexical_similarity(query, question) for question in self.questions]
            best_index = int(np.argmax(lexical_scores))
            best_score = float(lexical_scores[best_index])

        selected = self.faq_entries[best_index]
        escalated = best_score < self.threshold
        force_escalation = self._should_force_escalation(query, selected["intent"])

        if escalated or force_escalation:
            if selected["intent"] in self._forced_escalation_intents and best_score >= self.threshold:
                return MatchResult(
                    domain=selected["domain"],
                    intent=selected["intent"],
                    answer=selected["answer"],
                    confidence=round(best_score, 2),
                    escalated=True,
                )
            return MatchResult(
                domain="general",
                intent="unknown",
                answer=(
                    "I am not fully sure about this issue, so I will escalate it to human support."
                ),
                confidence=round(min(best_score, 0.49), 2),
                escalated=True,
            )

        return MatchResult(
            domain=selected["domain"],
            intent=selected["intent"],
            answer=selected["answer"],
            confidence=round(best_score, 2),
            escalated=False,
        )

    def ask(self, query: str) -> Dict[str, object]:
        result = self._find_best_faq(query=query)
        return {
            "query": query,
            "domain": result.domain,
            "intent": result.intent,
            "response": result.answer,
            "confidence": result.confidence,
            "escalated": result.escalated,
        }
