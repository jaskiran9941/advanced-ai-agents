"""
tools.py — Level 2
==================
Five tools total. Claude chains them in whatever order makes sense
for the customer's request — you never tell it the sequence.

New tools vs Level 1:
  get_customer_profile    — fetch name, email, tier from customer_id
                            (Claude finds customer_id inside the order result)
  check_inventory         — is a replacement item in stock?
  process_return          — mark an order as return_requested in memory
  send_confirmation_email — mock email send (logs it, returns confirmation)
"""

import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.data import ORDERS, CUSTOMERS, INVENTORY

# ---------------------------------------------------------------------------
# Tool schemas — what Claude sees
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up a customer order by order ID. Returns status, items, "
            "customer_id, estimated delivery, tracking info, and any issues. "
            "Use this whenever a customer asks about their order or delivery."
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
            "Use the customer_id found inside an order result. "
            "Required before sending a confirmation email."
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
            "Check how many units of a product are in stock. "
            "Use the product_id from an order's items list. "
            "Call this before offering a replacement to confirm availability."
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
            "Initiate a return for an order. Marks it as return_requested. "
            "Only call this after confirming the order exists and is eligible "
            "(delivered or damaged — not cancelled or already returned)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "e.g. ORD-1001"},
                "reason": {"type": "string", "description": "Customer's reason for return"},
            },
            "required": ["order_id", "reason"],
        },
    },
    {
        "name": "send_confirmation_email",
        "description": (
            "Send a confirmation email to the customer. "
            "Use the email address from get_customer_profile. "
            "Call this as the final step after completing any action (return, exchange, etc.)."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "to_email": {"type": "string", "description": "Customer's email address"},
                "subject":  {"type": "string", "description": "Email subject line"},
                "body":     {"type": "string", "description": "Email body text"},
            },
            "required": ["to_email", "subject", "body"],
        },
    },
]

# ---------------------------------------------------------------------------
# Tool execution functions
# ---------------------------------------------------------------------------

def get_order_status(order_id: str) -> dict:
    order = ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"No order found with ID '{order_id}'."}
    return order


def get_customer_profile(customer_id: str) -> dict:
    customer = CUSTOMERS.get(customer_id.upper())
    if not customer:
        return {"error": f"No customer found with ID '{customer_id}'."}
    return customer


def check_inventory(product_id: str) -> dict:
    product = INVENTORY.get(product_id.upper())
    if not product:
        return {"error": f"No product found with ID '{product_id}'."}
    return {
        "product_id": product_id,
        "name": product["name"],
        "stock": product["stock"],
        "in_stock": product["stock"] > 0,
        "price": product["price"],
    }


def process_return(order_id: str, reason: str) -> dict:
    order = ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"No order found with ID '{order_id}'."}

    ineligible = ["cancelled", "return_requested", "returned"]
    if order["status"] in ineligible:
        return {"error": f"Order {order_id} cannot be returned (status: {order['status']})."}

    # Mutate in-memory mock data so it feels real within the session
    order["status"] = "return_requested"
    order["return_reason"] = reason

    return {
        "success": True,
        "order_id": order_id,
        "new_status": "return_requested",
        "message": f"Return initiated for {order_id}. Refund will be processed in 5-7 business days.",
    }


def send_confirmation_email(to_email: str, subject: str, body: str) -> dict:
    # Mock — no real email sent. Returns a confirmation record.
    return {
        "success": True,
        "to": to_email,
        "subject": subject,
        "status": "sent",
        "note": "[MOCK] No real email sent — this is a simulation.",
    }


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

TOOL_FUNCTIONS = {
    "get_order_status":       lambda i: get_order_status(i["order_id"]),
    "get_customer_profile":   lambda i: get_customer_profile(i["customer_id"]),
    "check_inventory":        lambda i: check_inventory(i["product_id"]),
    "process_return":         lambda i: process_return(i["order_id"], i["reason"]),
    "send_confirmation_email": lambda i: send_confirmation_email(i["to_email"], i["subject"], i["body"]),
}


def execute_tool(tool_name: str, tool_input: dict) -> str:
    fn = TOOL_FUNCTIONS.get(tool_name)
    if not fn:
        return f"Unknown tool: {tool_name}"
    return str(fn(tool_input))
