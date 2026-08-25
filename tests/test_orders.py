from src.tools.order_lookup import lookup_order, normalize_order_id


def test_valid_order():

    result = lookup_order("ORD-1007")

    assert result["found"]

    order = result["order"]

    assert order["status"] == "shipped"
    assert order["carrier"] == "UPS"


def test_lowercase_order():

    result = lookup_order("ord-1007")

    assert result["found"]


def test_whitespace_order_id():

    result = lookup_order("  ord-1007  ")

    assert result["found"]


def test_unknown_order():

    result = lookup_order("ORD-9999")

    assert not result["found"]
    assert result["reason"] == "not_found"


def test_random_unknown_order_does_not_alias_to_real_order():

    result = lookup_order("ORD-5555")

    assert not result["found"]


def test_invalid_order_id_format():

    result = lookup_order("12345")

    assert not result["found"]
    assert result["reason"] == "invalid_order_id"


def test_empty_order_id():

    result = lookup_order("")

    assert not result["found"]
    assert result["reason"] == "invalid_order_id"


def test_normalize_order_id():

    assert normalize_order_id("ord-1007") == "ORD-1007"
    assert normalize_order_id(" ORD-1007 ") == "ORD-1007"
    assert normalize_order_id("ORD-99") is None
    assert normalize_order_id("ORDER-1007") is None
    assert normalize_order_id(None) is None


def test_cancelled_order_does_not_expose_stale_eta():

    result = lookup_order("ORD-1004")

    order = result["order"]

    assert order["status"] == "cancelled"
    assert order["estimated_delivery"] is None
    assert order["carrier"] is None
    assert order["tracking_number"] is None


def test_returned_order_does_not_expose_stale_eta():

    result = lookup_order("ORD-1003")

    order = result["order"]

    assert order["status"] == "returned"
    assert order["estimated_delivery"] is None


def test_active_shipped_order_keeps_tracking_info():

    result = lookup_order("ORD-1007")

    order = result["order"]

    assert order["tracking_number"] is not None
    assert order["estimated_delivery"] is not None


def test_sensitive_fields_are_not_returned():

    result = lookup_order("ORD-1007")

    order = result["order"]

    assert "customer" not in order
    assert "internal_notes" not in order
    assert "risk_score" not in order
    assert "support_tags" not in order
