from typing import List, TypedDict


class FAQEntry(TypedDict):
    intent: str
    question: str
    answer: str


FAQ_ENTRIES: List[FAQEntry] = [
    {
        "intent": "order_status",
        "question": "Where is my order and how can I track it?",
        "answer": "You can track your order from the 'My Orders' section using your order ID. Tracking updates are usually available within a few hours of shipment.",
    },
    {
        "intent": "refund_policy",
        "question": "What is your refund policy?",
        "answer": "Refunds are processed for eligible items after return approval. Most refunds are completed to the original payment method within 5 to 7 business days.",
    },
    {
        "intent": "return_policy",
        "question": "How can I return a product?",
        "answer": "You can return eligible products within 7 days of delivery from the returns section in your account. Please keep the item in original condition with packaging.",
    },
    {
        "intent": "delivery_time",
        "question": "How long does delivery take?",
        "answer": "Standard delivery usually takes 3 to 5 business days, while express delivery takes 1 to 2 business days depending on your location.",
    },
    {
        "intent": "cancel_order",
        "question": "How do I cancel my order?",
        "answer": "You can cancel an order before it is shipped from 'My Orders'. If the order is already shipped, you can request a return after delivery.",
    },
    {
        "intent": "payment_failure",
        "question": "Why did my payment fail?",
        "answer": "Payment failures can happen due to insufficient balance, bank verification, network timeouts, or incorrect card details. Please retry or use a different payment method.",
    },
    {
        "intent": "product_availability",
        "question": "Is this product in stock?",
        "answer": "Product availability is shown on each product page. If an item is out of stock, you can enable stock alerts to get notified when it is available again.",
    },
    {
        "intent": "shipping_charges",
        "question": "What are the shipping charges?",
        "answer": "Shipping charges depend on location, cart value, and delivery speed. Many orders above a minimum cart amount qualify for free standard shipping.",
    },
    {
        "intent": "damaged_product",
        "question": "I received a damaged product, what should I do?",
        "answer": "We are sorry about that. Please submit a damage report with photos within 48 hours of delivery so we can arrange a replacement or refund.",
    },
    {
        "intent": "exchange_policy",
        "question": "Can I exchange an item?",
        "answer": "Yes, exchange is available for eligible products and sizes within the return window. Exchange options appear in the order details page.",
    },
    {
        "intent": "account_login_issue",
        "question": "I cannot log in to my account.",
        "answer": "Please try resetting your password using 'Forgot Password'. If you still cannot access your account, contact support for secure account verification.",
    },
    {
        "intent": "coupon_issue",
        "question": "My discount coupon is not working.",
        "answer": "Please check coupon validity dates, minimum order value, and eligible categories. Coupons may not apply to already discounted items.",
    },
    {
        "intent": "warranty_info",
        "question": "Does this product have a warranty?",
        "answer": "Warranty coverage depends on the product and seller. Warranty details are listed on the product page and invoice when applicable.",
    },
    {
        "intent": "contact_support",
        "question": "How can I contact customer support?",
        "answer": "You can contact support via live chat, email, or phone through the Help Center. Please share your order ID for faster assistance.",
    },
    {
        "intent": "invoice_request",
        "question": "How can I download my invoice or bill?",
        "answer": "Invoices are available in the order details section after your order is confirmed. Select the order and click 'Download Invoice'.",
    },
]
