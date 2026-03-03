"""
tools.py — Level 3
==================
Same 5 tools as Level 2 + one new one: search_policies.

search_policies lets Claude retrieve the actual Acme Shop policy text
instead of relying on its training data. The difference:
  - Level 2: "Can I return after 45 days?" → Claude guesses from training
  - Level 3: Claude calls search_policies → reads the real policy → answers accurately
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.data import ORDERS, CUSTOMERS, INVENTORY
from knowledge import search_policies as _search_policies

# ---------------------------------------------------------------------------
# Tool schemas
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up a customer order by order ID. Returns status, items, "
            "customer_id, estimated delivery, tracking info, and any issues."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. ORD-1001"}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "get_customer_profile",
        "description": (
            "Fetch a customer's profile (name, email, tier, preferred contact). "
            "Use the customer_id found inside an order result."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "e.g. CUST-001"}
            },
            "required": ["customer_id"],
        },
    },
    {
        "name": "check_inventory",
        "description": (
            "Check stock levels for a product by product_id. "
            "Call before offering a replacement."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "e.g. PROD-A"}
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "process_return",
        "description": (
            "Initiate a return for a delivered or damaged order. "
            "Only call after confirming the order exists and is eligible."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string"},
                "reason":   {"type": "string"},
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "send_confirmation_email",
        "description": (
            "Send a confirmation email to the customer. "
            "Always get the email from get_customer_profile first."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string"},
                "subject":  {"type": "string"},
                "body":     {"type": "string"},
            },
            "required": ["to_email", "subject", "body"],
        },
    },
    {
        "name": "search_policies",
        "description": (
            "Search Acme Shop's official policy documents (returns, shipping, "
            "refunds, warranty, billing) using semantic search. "
            "Use this whenever a customer asks about policy, eligibility, timelines, "
            "or anything that requires an official answer — don't rely on guesswork."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "A natural-language description of what policy to look up.",
                }
            },
            "required": ["query"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool execution
# ---------------------------------------------------------------------------

def get_order_status(order_id):
    order = ORDERS.get(order_id.upper())
    return order or {"error": f"No order found with ID '{order_id}'."}

def get_customer_profile(customer_id):
    customer = CUSTOMERS.get(customer_id.upper())
    return customer or {"error": f"No customer found with ID '{customer_id}'."}

def check_inventory(product_id):
    product = INVENTORY.get(product_id.upper())
    if not product:
        return {"error": f"No product found with ID '{product_id}'."}
    return {"product_id": product_id, "name": product["name"],
            "stock": product["stock"], "in_stock": product["stock"] > 0, "price": product["price"]}

def process_return(order_id, reason):
    order = ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"No order found with ID '{order_id}'."}
    if order["status"] in ["cancelled", "return_requested", "returned"]:
        return {"error": f"Order {order_id} cannot be returned (status: {order['status']})."}
    order["status"] = "return_requested"
    order["return_reason"] = reason
    return {"success": True, "order_id": order_id, "new_status": "return_requested",
            "message": "Return initiated. Refund processed in 5-7 business days."}

def send_confirmation_email(to_email, subject, body):
    return {"success": True, "to": to_email, "subject": subject,
            "status": "sent", "note": "[MOCK] No real email sent."}

def search_policies(query):
    hits = _search_policies(query, n_results=2)
    return hits


TOOL_FUNCTIONS = {
    "get_order_status":        lambda i: get_order_status(i["order_id"]),
    "get_customer_profile":    lambda i: get_customer_profile(i["customer_id"]),
    "check_inventory":         lambda i: check_inventory(i["product_id"]),
    "process_return":          lambda i: process_return(i["order_id"], i["reason"]),
    "send_confirmation_email": lambda i: send_confirmation_email(i["to_email"], i["subject"], i["body"]),
    "search_policies":         lambda i: search_policies(i["query"]),
}

def execute_tool(tool_name, tool_input):
    fn = TOOL_FUNCTIONS.get(tool_name)
    if not fn:
        return f"Unknown tool: {tool_name}"
    return str(fn(tool_input))
