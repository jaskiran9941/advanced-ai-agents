"""
agents/technical.py — Level 7
"""
import os, sys, anthropic
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from level7_langgraph.state import SupportState

TECHNICAL_TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up order details and damage/defect notes.",
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
    },
    {
        "name": "check_inventory",
        "description": "Check stock levels for a replacement product.",
        "input_schema": {"type": "object", "properties": {"product_id": {"type": "string"}}, "required": ["product_id"]},
    },
    {
        "name": "search_policies",
        "description": "Search Acme Shop warranty and return policy documents.",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
]

TECHNICAL_SYSTEM = """You are the Technical specialist at Acme Shop support.
Your domain: product defects, warranty claims, replacements, troubleshooting.

IMPORTANT: When you check inventory for a replacement, include this line:
  REPLACEMENT_PRODUCT: <product_id>
  REPLACEMENT_IN_STOCK: <true|false>

For example:
  REPLACEMENT_PRODUCT: PROD-D
  REPLACEMENT_IN_STOCK: true

Always check warranty policy before making claims."""


def run(state: SupportState, on_step=None) -> dict:
    import re
    from level7_langgraph.tools import execute_tool
    client   = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    context  = state.get("technical_context", "")
    ticket   = state["ticket"]
    messages = [{"role": "user", "content": f"{context}\n\nCustomer ticket: {ticket}".strip()}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            system=TECHNICAL_SYSTEM, tools=TECHNICAL_TOOLS, messages=messages,
        )
        if on_step:
            on_step("agent_call", {"agent": "technical", "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens})
        if response.stop_reason == "end_turn":
            text = next(b.text for b in response.content if b.type == "text")
            # Extract structured values from agent response
            prod_match  = re.search(r"REPLACEMENT_PRODUCT:\s*(\S+)", text)
            stock_match = re.search(r"REPLACEMENT_IN_STOCK:\s*(true|false)", text, re.IGNORECASE)
            return {
                "technical_result":      text,
                "replacement_product_id": prod_match.group(1) if prod_match else "",
                "replacement_in_stock":   stock_match.group(1).lower() == "true" if stock_match else False,
            }
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if on_step:
                    on_step("tool_call", {"agent": "technical", "tool": block.name, "input": block.input})
                result = execute_tool(block.name, block.input)
                if on_step:
                    on_step("tool_result", {"agent": "technical", "tool": block.name, "result": result})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "user", "content": tool_results})
