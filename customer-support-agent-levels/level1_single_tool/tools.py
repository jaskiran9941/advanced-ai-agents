"""
tools.py — Level 1
==================
One tool: get_order_status

Two things live here:
  1. TOOL_SCHEMAS  — the JSON description Claude reads to know the tool exists
                     and what arguments to pass. This is what you put in the
                     `tools=` parameter of the API call.
  2. execute_tool  — the actual Python function that runs when Claude calls it.
                     Claude never runs code directly; it asks us to, then we
                     send the result back.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.data import ORDERS

# ---------------------------------------------------------------------------
# 1. Tool schema — Claude reads this to decide when and how to call the tool
# ---------------------------------------------------------------------------

TOOL_SCHEMAS = [
    {
        "name": "get_order_status",
        "description": (
            "Look up the current status of a customer order by order ID. "
            "Returns status, items, estimated delivery, tracking info, and any delay/damage notes. "
            "Use this whenever a customer asks about their order, delivery, or tracking."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order ID, e.g. ORD-1001. Ask the customer if they haven't provided it.",
                }
            },
            "required": ["order_id"],
        },
    }
]

# ---------------------------------------------------------------------------
# 2. Tool execution — runs when Claude decides to call get_order_status
# ---------------------------------------------------------------------------

def get_order_status(order_id: str) -> dict:
    """Look up an order from our mock data store."""
    order = ORDERS.get(order_id.upper())
    if not order:
        return {"error": f"No order found with ID '{order_id}'. Please check the order ID and try again."}
    return order


def execute_tool(tool_name: str, tool_input: dict) -> str:
    """
    Dispatcher: given a tool name + input dict from Claude,
    call the right Python function and return a string result.
    Claude expects the result as a string in the tool_result message.
    """
    if tool_name == "get_order_status":
        result = get_order_status(tool_input["order_id"])
        return str(result)
    return f"Unknown tool: {tool_name}"
