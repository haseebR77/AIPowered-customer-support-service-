from backend.chatbot import SupportChatbot


def test_order_tracking_intent():
    bot = SupportChatbot()
    result = bot.ask("Where is my order?")
    assert result["intent"] == "order_status"


def test_refund_intent():
    bot = SupportChatbot()
    result = bot.ask("When will I get my refund?")
    assert result["intent"] == "refund_policy"


def test_return_intent():
    bot = SupportChatbot()
    result = bot.ask("How can I return this product?")
    assert result["intent"] == "return_policy"


def test_delivery_intent():
    bot = SupportChatbot()
    result = bot.ask("How long does delivery take?")
    assert result["intent"] == "delivery_time"


def test_payment_failure_intent():
    bot = SupportChatbot()
    result = bot.ask("My payment is failing")
    assert result["intent"] == "payment_failure"


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

