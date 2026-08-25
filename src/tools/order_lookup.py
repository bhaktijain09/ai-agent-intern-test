import json
import re
from src.config import ORDERS_FILE


CUSTOMER_SAFE_FIELDS = {
    "order_id",
    "membership_tier",
    "items",
    "placed_at",
    "status",
    "status_updated_at",
    "shipped_at",
    "delivered_at",
    "carrier",
    "tracking_number",
    "estimated_delivery",
    "customer_safe_message"
}


def normalize_order_id(order_id: str):

    if not order_id:
        return None

    order_id = order_id.strip().upper()

    match = re.fullmatch(
        r"ORD-\d{4}",
        order_id
    )

    if not match:
        return None

    return order_id


_ORDERS_CACHE = None


def load_orders(force_reload=False):

    global _ORDERS_CACHE

    if _ORDERS_CACHE is not None and not force_reload:
        return _ORDERS_CACHE

    with open(
        ORDERS_FILE,
        "r",
        encoding="utf-8"
    ) as f:
        data = json.load(f)

    _ORDERS_CACHE = data["orders"]

    return _ORDERS_CACHE


def sanitize_order(order):

    result = {
        key: order[key]
        for key in CUSTOMER_SAFE_FIELDS
        if key in order
    }

    # Critical status precedence: a cancelled or returned order can never
    # be described (or misread by the LLM) as still in transit.
    status = order["status"]

    if status in {"cancelled", "returned"}:

        result["carrier"] = None
        result["tracking_number"] = None
        result["estimated_delivery"] = None

    return result


def lookup_order(order_id):

    normalized = normalize_order_id(order_id)

    if not normalized:
        return {
            "found": False,
            "reason": "invalid_order_id"
        }

    orders = load_orders()

    for order in orders:

        if order["order_id"] == normalized:

            return {
                "found": True,
                "order": sanitize_order(order)
            }

    return {
        "found": False,
        "reason": "not_found"
    }
