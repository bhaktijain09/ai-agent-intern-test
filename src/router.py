import re


ORDER_PATTERN = r"\bORD-\d{4}\b"

ORDER_WORDS = [
    "order",
    "tracking",
    "delivery",
    "arrive",
    "arriving",
    "shipped",
    "shipment",
    "package",
]


def extract_order_id(text):

    match = re.search(
        ORDER_PATTERN,
        text.upper()
    )

    return match.group(0) if match else None


def route_request(text):

    lower = text.lower()

    order_id = extract_order_id(text)

    if order_id:
        return "order"

    if any(word in lower for word in ORDER_WORDS):
        return "order_missing_id"

    return "knowledge"
