"""
agents/shipping.py — Level 7
"""
import os, sys, anthropic
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from level7_langgraph.state import SupportState

SHIPPING_TOOLS = [
    {
        "name": "get_order_status",
        "description": "Look up order tracking, carrier, and delivery status.",
        "input_schema": {"type": "object", "properties": {"order_id": {"type": "string"}}, "required": ["order_id"]},
    },
    {
        "name": "search_policies",
        "description": "Search Acme Shop shipping and delivery policy documents.",
        "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]},
    },
]

SHIPPING_SYSTEM = """You are the Shipping specialist at Acme Shop support.
Your domain: delivery tracking, shipping delays, carrier issues, ETAs, shipping policies.
Always cite tracking numbers, carrier names, and estimated dates."""


def run(state: SupportState, on_step=None) -> dict:
    from level7_langgraph.tools import execute_tool
    client   = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), max_retries=5)
    context  = state.get("shipping_context", "")
    ticket   = state["ticket"]
    messages = [{"role": "user", "content": f"{context}\n\nCustomer ticket: {ticket}".strip()}]

    while True:
        response = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1024,
            system=SHIPPING_SYSTEM, tools=SHIPPING_TOOLS, messages=messages,
        )
        if on_step:
            on_step("agent_call", {"agent": "shipping", "stop_reason": response.stop_reason,
                "input_tokens": response.usage.input_tokens, "output_tokens": response.usage.output_tokens})
        if response.stop_reason == "end_turn":
            return {"shipping_result": next(b.text for b in response.content if b.type == "text")}
        if response.stop_reason == "tool_use":
            messages.append({"role": "assistant", "content": response.content})
            tool_results = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if on_step:
                    on_step("tool_call", {"agent": "shipping", "tool": block.name, "input": block.input})
                result = execute_tool(block.name, block.input)
                if on_step:
                    on_step("tool_result", {"agent": "shipping", "tool": block.name, "result": result})
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": result})
            messages.append({"role": "user", "content": tool_results})
