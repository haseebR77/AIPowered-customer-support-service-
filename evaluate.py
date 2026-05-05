from backend.chatbot import SupportChatbot

TEST_CASES = [
    {"query": "Track my order please", "expected_intent": "order_status"},
    {"query": "When will I get my refund", "expected_intent": "refund_policy"},
    {"query": "I want to return an item", "expected_intent": "return_policy"},
    {"query": "How many days for delivery", "expected_intent": "delivery_time"},
    {"query": "Can I cancel an order", "expected_intent": "cancel_order"},
    {"query": "Payment is failing every time", "expected_intent": "payment_failure"},
    {"query": "Is this item available now", "expected_intent": "product_availability"},
    {"query": "What are shipping fees", "expected_intent": "shipping_charges"},
    {"query": "My product came damaged", "expected_intent": "damaged_product"},
    {"query": "How do I get my invoice", "expected_intent": "invoice_request"},
    {"query": "Coupon code does not apply", "expected_intent": "coupon_issue"},
    {"query": "Need to exchange for another size", "expected_intent": "exchange_policy"},
]


def evaluate() -> None:
    bot = SupportChatbot(threshold=0.62)

    total = len(TEST_CASES)
    correct = 0

    print("Running FAQ intent evaluation...")
    print("-" * 60)

    for idx, case in enumerate(TEST_CASES, start=1):
        result = bot.ask(case["query"])
        predicted = result["intent"]
        expected = case["expected_intent"]
        is_correct = predicted == expected

        if is_correct:
            correct += 1

        print(
            f"{idx:02d}. Query: {case['query']}\n"
            f"    Predicted: {predicted} | Expected: {expected} | "
            f"Confidence: {result['confidence']:.2f} | Correct: {is_correct}"
        )

    accuracy = (correct / total) * 100 if total else 0.0

    print("-" * 60)
    print(f"Total test queries: {total}")
    print(f"Correct predictions: {correct}")
    print(f"Accuracy percentage: {accuracy:.2f}%")


if __name__ == "__main__":
    evaluate()
