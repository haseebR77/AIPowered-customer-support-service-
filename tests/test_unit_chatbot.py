from backend.chatbot import SupportChatbot


def test_order_tracking_intent():
    bot = SupportChatbot()
    result = bot.ask("Where is my order?")
    assert result["intent"] == "order_status"
    assert result["domain"] == "ecommerce"


def test_refund_intent():
    bot = SupportChatbot()
    result = bot.ask("I want a refund.")
    assert result["intent"] == "refund_request"
    assert result["domain"] == "ecommerce"


def test_return_intent():
    bot = SupportChatbot()
    result = bot.ask("How can I return this product?")
    assert result["intent"] == "return_policy"
    assert result["domain"] == "ecommerce"


def test_healthcare_appointment_intent():
    bot = SupportChatbot()
    result = bot.ask("How can I book a doctor appointment?")
    assert result["intent"] == "appointment_booking"
    assert result["domain"] == "healthcare"


def test_banking_pin_reset_intent():
    bot = SupportChatbot()
    result = bot.ask("How can I reset my ATM PIN?")
    assert result["intent"] == "atm_pin_reset"
    assert result["domain"] == "banking"


def test_known_faq_response_is_non_empty():
    bot = SupportChatbot()
    result = bot.ask("How can I download my invoice?")
    assert isinstance(result["response"], str)
    assert result["response"].strip() != ""


def test_unknown_query_escalates_with_high_threshold():
    # High threshold ensures low-similarity unknown queries escalate safely.
    bot = SupportChatbot(threshold=0.99)
    result = bot.ask("xqzv unrelated technical incident not in faq")
    assert result["escalated"] is True
    assert result["intent"] == "unknown"
    assert result["domain"] == "general"


def test_forced_escalation_for_urgent_medical_help():
    bot = SupportChatbot()
    result = bot.ask("I need urgent medical help.")
    assert result["intent"] == "urgent_medical_help"
    assert result["domain"] == "healthcare"
    assert result["escalated"] is True

