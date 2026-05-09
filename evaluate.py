from backend.chatbot import SupportChatbot

TEST_CASES = [
    {"query": "Track my order please", "expected_domain": "ecommerce", "expected_intent": "order_status"},
    {"query": "I want a refund for my order", "expected_domain": "ecommerce", "expected_intent": "refund_request"},
    {"query": "How can I return this product", "expected_domain": "ecommerce", "expected_intent": "return_policy"},
    {"query": "How long does delivery take", "expected_domain": "ecommerce", "expected_intent": "delivery_info"},
    {"query": "What payment options are available", "expected_domain": "ecommerce", "expected_intent": "payment_methods"},
    {"query": "Book a doctor appointment", "expected_domain": "healthcare", "expected_intent": "appointment_booking"},
    {"query": "Share your clinic timings", "expected_domain": "healthcare", "expected_intent": "clinic_timings"},
    {"query": "Do you offer online consultation", "expected_domain": "healthcare", "expected_intent": "online_consultation"},
    {"query": "I need urgent medical help", "expected_domain": "healthcare", "expected_intent": "urgent_medical_help"},
    {"query": "How can I reset my atm pin", "expected_domain": "banking", "expected_intent": "atm_pin_reset"},
    {"query": "My card is blocked please help", "expected_domain": "banking", "expected_intent": "card_blocked"},
    {"query": "There is an unknown transaction", "expected_domain": "banking", "expected_intent": "unknown_transaction"},
]


def evaluate() -> None:
    bot = SupportChatbot(threshold=0.50)

    total = len(TEST_CASES)
    correct_intent = 0
    correct_domain = 0

    print("Running multi-domain intent evaluation...")
    print("-" * 60)

    for idx, case in enumerate(TEST_CASES, start=1):
        result = bot.ask(case["query"])
        predicted = result["intent"]
        predicted_domain = result["domain"]
        expected = case["expected_intent"]
        expected_domain = case["expected_domain"]
        is_intent_correct = predicted == expected
        is_domain_correct = predicted_domain == expected_domain

        if is_intent_correct:
            correct_intent += 1
        if is_domain_correct:
            correct_domain += 1

        print(
            f"{idx:02d}. Query: {case['query']}\n"
            f"    Domain: {predicted_domain} (expected {expected_domain}) | "
            f"Intent: {predicted} (expected {expected}) | "
            f"Confidence: {result['confidence']:.2f} | "
            f"Escalated: {result['escalated']}"
        )

    intent_accuracy = (correct_intent / total) * 100 if total else 0.0
    domain_accuracy = (correct_domain / total) * 100 if total else 0.0

    print("-" * 60)
    print(f"Total test queries: {total}")
    print(f"Correct domain predictions: {correct_domain}")
    print(f"Correct intent predictions: {correct_intent}")
    print(f"Domain accuracy percentage: {domain_accuracy:.2f}%")
    print(f"Intent accuracy percentage: {intent_accuracy:.2f}%")


if __name__ == "__main__":
    evaluate()
