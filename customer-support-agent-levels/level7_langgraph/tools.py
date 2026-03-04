"""tools.py — Level 7 (same tools as L6, shared)"""
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from shared.data import ORDERS, CUSTOMERS, INVENTORY
from level7_langgraph.knowledge import search_policies as _search_policies

def get_order_status(order_id):
    o = ORDERS.get(order_id.upper())
    return o or {"error": f"No order found: {order_id}"}

def get_customer_profile(customer_id):
    c = CUSTOMERS.get(customer_id.upper())
    return c or {"error": f"No customer found: {customer_id}"}

def check_inventory(product_id):
    p = INVENTORY.get(product_id.upper())
    if not p:
        return {"error": f"No product found: {product_id}"}
    return {"product_id": product_id, "name": p["name"], "stock": p["stock"],
            "in_stock": p["stock"] > 0, "price": p["price"]}

def process_return(order_id, reason):
    o = ORDERS.get(order_id.upper())
    if not o:
        return {"error": f"No order found: {order_id}"}
    if o["status"] in ["cancelled", "return_requested", "returned"]:
        return {"error": f"Cannot return order with status: {o['status']}"}
    o["status"] = "return_requested"
    o["return_reason"] = reason
    return {"success": True, "order_id": order_id, "new_status": "return_requested",
            "message": "Return initiated. Refund in 5-7 business days."}

def send_confirmation_email(to_email, subject, body):
    return {"success": True, "to": to_email, "subject": subject, "status": "sent"}

def search_policies(query):
    return _search_policies(query, n_results=2)

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
    return str(fn(tool_input)) if fn else f"Unknown tool: {tool_name}"
