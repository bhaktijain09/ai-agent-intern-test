# orders.json — Data Dictionary

This file documents every field in `data/orders.json` and marks which
fields are safe to expose to a customer through the support agent.

The agent must NEVER pass this raw file to the LLM. All access must
go through `src/tools/order_lookup.py`, which filters to
`CUSTOMER_SAFE_FIELDS` and sanitizes cancelled/returned orders.

| Field                   | Customer-safe? | Notes                                                            |
|-------------------------|:--------------:|-------------------------------------------------------------------|
| `order_id`              | ✅              | Format `ORD-####`                                                 |
| `customer.email`        | ❌              | PII — never expose                                                |
| `customer.name`         | ❌              | PII — never expose                                                |
| `customer.address`      | ❌              | PII — never expose                                                |
| `membership_tier`       | ✅              | `standard` or `row_plus`                                          |
| `items`                 | ✅              | List of `{sku, name, quantity, price}`                            |
| `placed_at`             | ✅              | ISO date order was placed                                         |
| `status`                | ✅              | One of: processing, shipped, delivered, cancelled, returned       |
| `status_updated_at`     | ✅              | ISO date/time of last status change                                |
| `shipped_at`            | ✅              | Null if not yet shipped                                           |
| `delivered_at`          | ✅              | Null if not yet delivered                                         |
| `carrier`               | ✅*             | Nulled by the tool if status is cancelled/returned                |
| `tracking_number`       | ✅*             | Nulled by the tool if status is cancelled/returned                |
| `estimated_delivery`    | ✅*             | Nulled by the tool if status is cancelled/returned                |
| `customer_safe_message` | ✅              | Optional human-support-written note, safe to surface verbatim     |
| `internal_notes`        | ❌              | Free-text ops notes — never expose                                |
| `risk_score`             | ❌              | Fraud/risk model output — never expose                            |
| `support_tags`          | ❌              | Internal triage tags — never expose                               |

`*` = customer-safe in principle, but the tool actively strips these
three fields to `null` whenever `status` is `cancelled` or `returned`,
so a stale in-transit date can never be read out as if the order were
still moving.
