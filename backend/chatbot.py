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
    intent: str
    answer: str
    confidence: float
    escalated: bool


class SupportChatbot:
    """FAQ matching chatbot using sentence embeddings with robust lexical fallbacks."""

    def __init__(self, threshold: float = 0.62) -> None:
        self.threshold = threshold
        self.faq_entries = FAQ_ENTRIES
        self.questions: List[str] = [entry["question"] for entry in self.faq_entries]
        self.intent_to_answer = {
            entry["intent"]: entry["answer"] for entry in self.faq_entries
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
            "refund_policy": ["refund", "money back", "refund policy", "refund status"],
            "return_policy": ["return", "send back", "return policy", "return item"],
            "delivery_time": ["delivery", "arrive", "shipping time", "how long", "days"],
            "cancel_order": ["cancel", "stop order", "cancel order"],
            "payment_failure": [
                "payment failed",
                "payment failure",
                "card declined",
                "transaction failed",
                "could not pay",
                "payment failing",
                "failing payment",
                "payment is failing",
            ],
            "product_availability": ["in stock", "available", "out of stock", "availability"],
            "shipping_charges": ["shipping charge", "shipping fee", "delivery fee", "shipping cost"],
            "damaged_product": ["damaged", "broken", "defective", "received damage"],
            "exchange_policy": ["exchange", "replace size", "swap item"],
            "account_login_issue": ["login", "log in", "sign in", "password reset", "account access"],
            "coupon_issue": ["coupon", "discount code", "promo code", "voucher"],
            "warranty_info": ["warranty", "guarantee", "covered"],
            "contact_support": [
                "contact support",
                "talk to agent",
                "customer service",
                "help center",
                "support",
            ],
            "invoice_request": ["invoice", "bill", "receipt", "tax invoice"],
        }

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

    def _find_best_faq(self, query: str) -> MatchResult:
        keyword_result = self._keyword_match(query)
        if keyword_result:
            intent, confidence = keyword_result
            return MatchResult(
                intent=intent,
                answer=self.intent_to_answer[intent],
                confidence=round(confidence, 2),
                escalated=False,
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

        if escalated:
            return MatchResult(
                intent="unknown",
                answer=(
                    "I could not confidently answer your query. "
                    "Your request has been escalated to a human support agent."
                ),
                confidence=round(best_score, 2),
                escalated=True,
            )

        return MatchResult(
            intent=selected["intent"],
            answer=selected["answer"],
            confidence=round(best_score, 2),
            escalated=False,
        )

    def ask(self, query: str) -> Dict[str, object]:
        result = self._find_best_faq(query=query)
        return {
            "query": query,
            "intent": result.intent,
            "response": result.answer,
            "confidence": result.confidence,
            "escalated": result.escalated,
        }
