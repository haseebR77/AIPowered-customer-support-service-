from typing import List, TypedDict


class FAQEntry(TypedDict):
    domain: str
    intent: str
    question: str
    answer: str


FAQ_ENTRIES: List[FAQEntry] = [
    {
        "domain": "ecommerce",
        "intent": "order_status",
        "question": "Where is my order?",
        "answer": "You can track your order using your order ID in the order tracking section.",
    },
    {
        "domain": "ecommerce",
        "intent": "refund_request",
        "question": "I want a refund.",
        "answer": "You can request a refund from your order details page. Refunds are processed according to the refund policy.",
    },
    {
        "domain": "ecommerce",
        "intent": "return_policy",
        "question": "How can I return a product?",
        "answer": "You can return your product by submitting a return request from your order details page.",
    },
    {
        "domain": "ecommerce",
        "intent": "delivery_info",
        "question": "How long does delivery take?",
        "answer": "Delivery usually takes a few business days depending on your location and selected shipping method.",
    },
    {
        "domain": "ecommerce",
        "intent": "payment_methods",
        "question": "What payment methods are accepted?",
        "answer": "We accept common payment methods such as debit cards, credit cards, bank transfer, and digital wallets.",
    },
    {
        "domain": "healthcare",
        "intent": "appointment_booking",
        "question": "How can I book a doctor appointment?",
        "answer": "You can book a doctor appointment by selecting your preferred doctor, date, and available time slot.",
    },
    {
        "domain": "healthcare",
        "intent": "clinic_timings",
        "question": "What are your clinic timings?",
        "answer": "Clinic timings are usually available on the clinic information page. Please check the latest schedule before visiting.",
    },
    {
        "domain": "healthcare",
        "intent": "online_consultation",
        "question": "Do you provide online consultation?",
        "answer": "Yes, online consultation may be available. You can choose online consultation while booking an appointment.",
    },
    {
        "domain": "healthcare",
        "intent": "cancel_appointment",
        "question": "How can I cancel my appointment?",
        "answer": "You can cancel your appointment from your appointment details page or by contacting clinic support.",
    },
    {
        "domain": "healthcare",
        "intent": "urgent_medical_help",
        "question": "I need urgent medical help.",
        "answer": "This appears to be urgent. Please contact emergency medical services or visit the nearest hospital immediately.",
    },
    {
        "domain": "banking",
        "intent": "atm_pin_reset",
        "question": "How can I reset my ATM PIN?",
        "answer": "You can reset your ATM PIN through the banking app, ATM machine, or by contacting customer support.",
    },
    {
        "domain": "banking",
        "intent": "card_blocked",
        "question": "My card is blocked.",
        "answer": "Your card may be blocked due to security reasons. Please contact bank support or use the banking app to request help.",
    },
    {
        "domain": "banking",
        "intent": "unknown_transaction",
        "question": "I found an unknown transaction.",
        "answer": "This issue should be reviewed by bank support. Please report the transaction immediately through your banking app or customer service.",
    },
    {
        "domain": "banking",
        "intent": "account_opening",
        "question": "How can I open a bank account?",
        "answer": "You can open a bank account by submitting your required documents through the bank branch or online banking portal.",
    },
    {
        "domain": "banking",
        "intent": "payment_failed",
        "question": "What should I do if my payment failed?",
        "answer": "If your payment failed, please check your balance, internet connection, and transaction status. If the amount was deducted, contact bank support.",
    },
]
